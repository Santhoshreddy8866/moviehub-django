from django.shortcuts import (
    render,
    get_object_or_404
)

from django.utils import timezone

from .models import Movie


def home(request):

    telugu_movies = Movie.objects.filter(
        language="TELUGU"
    )

    english_movies = Movie.objects.filter(
        language="ENGLISH"
    )

    hindi_movies = Movie.objects.filter(
        language="HINDI"
    )


    context = {

        "telugu_movies":
            telugu_movies,

        "english_movies":
            english_movies,

        "hindi_movies":
            hindi_movies,

    }


    return render(
        request,
        "movies/home.html",
        context
    )



def movie_detail(
    request,
    movie_id
):

    movie = get_object_or_404(
        Movie,
        id=movie_id
    )


    shows = (

        movie.shows

        .select_related(
            "screen__theatre"
        )

        .filter(
            show_date__gte=
            timezone.localdate()
        )

        .order_by(
            "show_date",
            "show_time"
        )

    )


    context = {

        "movie":
            movie,

        "shows":
            shows,

    }


    return render(
        request,
        "movies/movie_detail.html",
        context
    )