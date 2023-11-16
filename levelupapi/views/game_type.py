"""View module for handling requests about game types"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import GameType


class GameTypeView(ViewSet):
    """Level up game types view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single game type

        Returns:
            Response -- JSON serialized game type
        """
        # Use GET method of ORM to retrieve a single GameType
        game_type = GameType.objects.get(pk=pk)
        # GameType retrieved above is passed to the serializer
        serializer = GameTypeSerializer(game_type)
        # serializer.data is passed to the Response as the response body
        return Response(serializer.data)


    def list(self, request):
        """Handle GET requests to get all game types

        Returns:
            Response -- JSON serialized list of game types
        """
        game_types = GameType.objects.all()
        serializer = GameTypeSerializer(game_types, many=True)
        return Response(serializer.data)



class GameTypeSerializer(serializers.ModelSerializer):
    """JSON serializer for game types
    """
    class Meta:
        model = GameType
        fields = ('id', 'label')