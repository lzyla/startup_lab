from django.shortcuts import render, redirect, get_object_or_404
from .models import Character, Conversation, Message
from .forms import CharacterForm, MessageForm
from openai import OpenAI
import os
from dotenv import load_dotenv
from django.utils.timezone import now
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

load_dotenv()

def get_openai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def character_list(request):
    characters = Character.objects.all()
    return render(request, 'character_list.html', {'characters': characters})

def chat_view(request):
    if request.method == 'POST':
        conv_id = request.POST.get('conversation_id')
        character_id = request.POST.get('character_id')
        character = get_object_or_404(Character, id=character_id)
        
        if conv_id:
            conversation = get_object_or_404(Conversation, id=conv_id)
        else:
            conversation = Conversation.objects.create(character=character)
            Message.objects.create(
                conversation=conversation,
                is_user=False,
                content=f"Cześć, nazywam się Anna Szurniewska, jestem mentorką i inwestorką w inkubatorze Startup 3.0. Chętnie zapoznam się z Waszym pomysłem."
            )
        
        form = MessageForm(request.POST)
        if form.is_valid():
            user_message = form.save(commit=False)
            user_message.conversation = conversation
            user_message.is_user = True
            user_message.save()

            try:
                client = get_openai_client()
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": character.description},
                        {"role": "user", "content": user_message.content}
                    ]
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
        conversation = Conversation.objects.create(character=character)
        Message.objects.create(
            conversation=conversation,
            is_user=False,
            content=f"Cześć, nazywam się Anna Szurniewska, jestem mentorką i inwestorką w inkubatorze Startup 3.0. Chętnie zapoznam się z Waszym pomysłem."
        )
        messages = conversation.messages.all()
        return render(request, 'chat.html', {
            'character': character,
            'messages': messages,
            'form': MessageForm(),
            'conversation_id': conversation.id,
            'timestamp': now().timestamp(),
            'hide_navbar': True
        })

def admin_character_form(request, id=None):
    if id:
        instance = get_object_or_404(Character, id=id)
        title = f"Edytuj postać: {instance.name}"
    else:
        instance = None
        title = "Dodaj nową postać"
        
    if request.method == 'POST':
        form = CharacterForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('character_list')
    else:
        form = CharacterForm(instance=instance)
    
    return render(request, 'admin_character_form.html', {'form': form, 'title': title})

def admin_character_list(request):
    characters = Character.objects.all()
    return render(request, 'admin_character_list.html', {'characters': characters})

@csrf_exempt
def chat_api_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            character_id = data.get('character_id')
            user_text = data.get('message')

            character = get_object_or_404(Character, id=character_id)
            conversation = Conversation.objects.filter(character=character).order_by('-created_at').first()
            if conversation is None:
                conversation = Conversation.objects.create(character=character)
            
            Message.objects.create(conversation=conversation, is_user=True, content=user_text)

            client = get_openai_client()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": character.description},
                    {"role": "user", "content": user_text}
                ]
            )
            ai_text = response.choices[0].message.content.strip()

            Message.objects.create(conversation=conversation, is_user=False, content=ai_text)

            return JsonResponse({'response': ai_text})

        except Exception as e:
            print("API error:", e)
            return JsonResponse({'response': 'Wystąpił błąd po stronie serwera.'}, status=500)

    return JsonResponse({'error': 'Nieprawidłowa metoda'}, status=405)