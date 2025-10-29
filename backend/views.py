import os
import json
from typing import List

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from dotenv import load_dotenv
from openai import OpenAI

from .forms import CharacterForm, MessageForm
from .models import Character, Conversation, Message


load_dotenv()


def get_openai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def staff_required(view):
    return login_required(user_passes_test(lambda u: u.is_active and u.is_staff)(view))


def _conversation_session_key(character_id: int) -> str:
    return f"conversation_{character_id}"


def _create_greeting(conversation: Conversation, character: Character) -> None:
    greeting_text = character.greeting or character.header_description
    if greeting_text:
        Message.objects.create(
            conversation=conversation,
            is_user=False,
            content=greeting_text,
        )


def _get_or_create_conversation(request, character: Character) -> Conversation:
    session_key = _conversation_session_key(character.id)
    conversation_id = request.session.get(session_key)
    conversation = None
    if conversation_id:
        try:
            conversation = Conversation.objects.get(id=conversation_id, character=character)
        except Conversation.DoesNotExist:
            conversation = None

    if conversation is None:
        conversation = Conversation.objects.create(character=character)
        _create_greeting(conversation, character)
        request.session[session_key] = conversation.id

    return conversation


def _ensure_conversation_in_session(request, conversation: Conversation) -> None:
    session_key = _conversation_session_key(conversation.character_id)
    request.session[session_key] = conversation.id


MAX_HISTORY_LENGTH = 12


def _build_message_payload(conversation: Conversation, character: Character) -> List[dict]:
    history = list(
        conversation.messages.order_by('-timestamp')[:MAX_HISTORY_LENGTH]
    )
    history.reverse()

    messages = [{"role": "system", "content": character.description}]
    for msg in history:
        role = "user" if msg.is_user else "assistant"
        messages.append({"role": role, "content": msg.content})
    return messages


def character_list(request):
    characters = Character.objects.all()
    return render(request, 'character_list.html', {'characters': characters})


def chat_view(request):
    if request.method == 'POST':
        conv_id = request.POST.get('conversation_id')
        character_id = request.POST.get('character_id')
        character = get_object_or_404(Character, id=character_id)
        
        conversation = None
        if conv_id:
            conversation = Conversation.objects.filter(id=conv_id, character=character).first()
        if conversation is None:
            conversation = _get_or_create_conversation(request, character)
        else:
            _ensure_conversation_in_session(request, conversation)
        
        form = MessageForm(request.POST)
        if form.is_valid():
            user_message = form.save(commit=False)
            user_message.conversation = conversation
            user_message.is_user = True
            user_message.save()

            try:
                client = get_openai_client()
                payload = _build_message_payload(conversation, character)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=payload,
                )
                ai_response = response.choices[0].message.content.strip()
            except Exception as e:
                print("GPT ERROR:", e)
                ai_response = "Wystąpił błąd podczas komunikacji z GPT."

            Message.objects.create(
                conversation=conversation,
                is_user=False,
                content=ai_response
            )

        messages = conversation.messages.all()
        return render(request, 'chat.html', {
            'character': character,
            'messages': messages,
            'form': MessageForm(),
            'conversation_id': conversation.id,
            'hide_navbar': True
        })

    else:
        character_id = request.GET.get('character_id')
        character = get_object_or_404(Character, id=character_id)
        conversation = _get_or_create_conversation(request, character)
        messages = conversation.messages.all()
        return render(request, 'chat.html', {
            'character': character,
            'messages': messages,
            'form': MessageForm(),
            'conversation_id': conversation.id,
            'timestamp': now().timestamp(),
            'hide_navbar': True
        })

@staff_required
def admin_character_form(request, id=None):
    if id:
        instance = get_object_or_404(Character, id=id)
        title = f"Edytuj postać: {instance.name}"
    else:
        instance = None
        title = "Dodaj nową postać"
        
    if request.method == 'POST':
        form = CharacterForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('character_list')
    else:
        form = CharacterForm(instance=instance)
    
    return render(request, 'admin_character_form.html', {'form': form, 'title': title})

@staff_required
def admin_character_list(request):
    characters = Character.objects.all()
    return render(request, 'admin_character_list.html', {'characters': characters})

@require_POST
def chat_api_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Nieprawidłowe dane'}, status=400)

    character_id = data.get('character_id')
    conversation_id = data.get('conversation_id')
    user_text = (data.get('message') or '').strip()

    if not character_id or not conversation_id or not user_text:
        return JsonResponse({'error': 'Brak wymaganych danych'}, status=400)

    if len(user_text) > 2000:
        return JsonResponse({'error': 'Wiadomość jest za długa'}, status=400)

    try:
        character_id = int(character_id)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Nieprawidłowe ID postaci'}, status=400)

    character = get_object_or_404(Character, id=character_id)
    session_key = _conversation_session_key(character.id)
    session_conversation_id = request.session.get(session_key)

    try:
        conversation_id = int(conversation_id)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Nieprawidłowe ID konwersacji'}, status=400)

    if session_conversation_id is None or conversation_id != int(session_conversation_id):
        return JsonResponse({'error': 'Nieautoryzowany dostęp do konwersacji'}, status=403)

    conversation = get_object_or_404(Conversation, id=conversation_id, character=character)

    Message.objects.create(conversation=conversation, is_user=True, content=user_text)

    try:
        client = get_openai_client()
        payload = _build_message_payload(conversation, character)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=payload,
        )
        ai_text = response.choices[0].message.content.strip()
    except Exception as e:
        print("API error:", e)
        ai_text = "Wystąpił błąd po stronie serwera."

    Message.objects.create(conversation=conversation, is_user=False, content=ai_text)

    return JsonResponse({'response': ai_text})
