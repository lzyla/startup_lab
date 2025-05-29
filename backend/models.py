from django.db import models

class Character(models.Model):
    name = models.CharField(max_length=200)
    header_description = models.TextField(blank=True, null=True)  # opis postaci (krótki opis)
    description = models.TextField()  # opis i instrukcje dla GPT
    avatar_url = models.URLField(blank=True, null=True)  # nowe pole, jeśli potrzebujesz

    class Meta:
        verbose_name = "Postać AI"
        verbose_name_plural = "Postacie AI"
    
    def __str__(self):
        return self.name

class Conversation(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Konwersacja"
        verbose_name_plural = "Konwersacje"
    
    def __str__(self):
        return f"Rozmowa z {self.character.name} ({self.created_at.strftime('%d-%m-%Y, %H:%M')})"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    is_user = models.BooleanField(default=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Wiadomość"
        verbose_name_plural = "Wiadomości"
        ordering = ['timestamp']
    
    def __str__(self):
        sender = "Użytkownik" if self.is_user else self.conversation.character.name
        return f"{sender}: {self.content[:30]}..."
