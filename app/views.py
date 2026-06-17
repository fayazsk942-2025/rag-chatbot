from django.shortcuts import render, redirect, HttpResponse, get_object_or_404

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .models import *

from .rag import (
    process_document,
    ask_question
)

import os

def landing(request):

    return render(
        request,
        'landing.html'
    )


from django.contrib.auth.models import User
from django.shortcuts import render, redirect

def register(request):

    if request.method == "POST":

        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm = request.POST["confirm"]

        if password != confirm:

            return render(
                request,
                "register.html",
                {
                    "error": "Passwords do not match"
                }
            )

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "register.html",
                {
                    "error": "Username already exists"
                }
            )

        User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password
        )

        return redirect("login")

    return render(
        request,
        "register.html"
    )

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        print("USERNAME:", username)
        print("PASSWORD:", password)

        user = authenticate(
            request,
            username=username,
            password=password
        )

        print("USER:", user)

        if user is not None:

            login(request, user)

            return redirect("home")

        else:

            return render(
                request,
                "login.html",
                {"error": "Invalid username or password"}
            )

    return render(request, "login.html")


def logout_view(request):

    logout(request)

    return redirect('landing')


def home(request):

    return render(
        request,
        'home.html'
    )


from .models import Profile

def profile(request):
    profile_obj, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if "image" in request.FILES:
            profile_obj.image = request.FILES["image"]
            profile_obj.save()

            return redirect("profile")

    return render(request, "profile.html", {
        "profile": profile_obj
    })

def upload_document(request):

    if request.method == "POST":

        uploaded_file = request.FILES["document"]

        allowed_extensions = [
            ".pdf",
            ".docx",
            ".txt"
        ]

        extension = os.path.splitext(
            uploaded_file.name
        )[1].lower()

        if extension not in allowed_extensions:

            return render(
                request,
                "upload.html",
                {
                    "error":
                    "Only PDF, DOCX and TXT files are allowed."
                }
            )

        doc = UploadedDocument.objects.create(
            user=request.user,
            file=uploaded_file
        )

        try:

            process_document(
                doc.file.path,
                doc.id
            )

        except Exception as e:

            doc.delete()

            return render(
                request,
                "upload.html",
                {
                    "error": str(e)
                }
            )

        session = ChatSession.objects.create(
            user=request.user,
            document=doc,
            title=uploaded_file.name
        )

        request.session["session_id"] = (
            session.id
        )

        return redirect("chat")

    return render(
        request,
        "upload.html"
    )

def chat_view(request):

    session_id = request.session.get("session_id")

    if not session_id:
        return redirect("upload_document")

    try:
        session = ChatSession.objects.get(
            id=session_id,
            user=request.user
        )
    except ChatSession.DoesNotExist:
        return redirect("upload_document")

    messages = ChatMessage.objects.filter(
        session=session
    ).order_by("id")

    chats = ChatSession.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "chat.html",
        {
            "messages": messages,
            "session": session,
            "chats": chats
        }
    )

import os

def send_message(request):

    if request.method == "POST":

        question = request.POST.get("message")

        session = ChatSession.objects.get(
            id=request.session["session_id"]
        )

        if session.title == "New Chat":

            session.title = question[:40]

            session.save()

        ChatMessage.objects.create(
            session=session,
            role="user",
            message=question
        )
        faiss_path = f"faiss_indexes/document_{session.document.id}"

        if not os.path.exists(
            os.path.join(faiss_path, "index.faiss")
        ):
            ChatMessage.objects.create(
                session=session,
                role="ai",
                message="Document index not found."
            )

            return redirect("chat")
        
        print("SESSION ID =", session.id)
        print("DOCUMENT ID =", session.document.id)

        print(
            "FAISS FILE =",
            os.path.exists(
                f"faiss_indexes/document_{session.document.id}/index.faiss"
            )
        )

        answer = ask_question(
        question,
        session.document.id
    )

        ChatMessage.objects.create(
            session=session,
            role="ai",
            message=answer
        )

        return redirect("chat")
    

def delete_chat(request, chat_id):

    ChatSession.objects.filter(
        id=chat_id,
        user=request.user
    ).delete()

    remaining = ChatSession.objects.filter(
        user=request.user
    ).order_by("-created_at")

    if remaining.exists():

        request.session["session_id"] = (
            remaining.first().id
        )

        return redirect("chat")

    request.session.pop(
        "session_id",
        None
    )

    return redirect("upload")

from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .models import ChatSession, ChatMessage


def share_chat(request, chat_id):
    chat = get_object_or_404(ChatSession, id=chat_id)

    share_url = request.build_absolute_uri(
        reverse("shared_chat", args=[chat.id])
    )

    return render(request, "share_chat.html", {
        "chat": chat,
        "share_url": share_url
    })


def shared_chat(request, chat_id):
    chat = get_object_or_404(ChatSession, id=chat_id)

    messages = ChatMessage.objects.filter(session=chat).order_by("created_at")

    return render(request, "shared_chat_view.html", {
        "chat": chat,
        "messages": messages,
        "is_shared": True
    })

def open_chat(request, chat_id):

    session = ChatSession.objects.get(
        id=chat_id,
        user=request.user
    )

    request.session["session_id"] = session.id

    return redirect("chat")

def new_chat(request):

    current_session = ChatSession.objects.get(
        id=request.session["session_id"]
    )

    new_session = ChatSession.objects.create(
        user=request.user,
        document=current_session.document,
        title="New Chat"
    )

    request.session["session_id"] = new_session.id

    return redirect("chat")