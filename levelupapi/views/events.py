"""View module for handling requests about events"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Event, Gamer, Game, EventGamer
from rest_framework.decorators import action

class EventView(ViewSet):
    """Level up events view"""

    ########################
    ######## CREATE ########
    ########################
    
    def create(self, request):
        """Handle POST operations

        Returns
            Response -- JSON serialized event instance
        """
        gamer = Gamer.objects.get(pk=request.data["organizer"])
        game = Game.objects.get(pk=request.data["game"])

        event = Event.objects.create(
            game=game,
            description=request.data["description"],
            date=request.data["date"],
            time=request.data["time"],
            organizer=gamer,
        )
        serializer = EventSerializer(event)
        return Response(serializer.data)
    
    
    
    ########################
    ######### READ #########
    ########################
    
    def retrieve(self, request, pk):
        """Handle GET requests for single event
        
        Returns:
            Response -- JSON serialized event
        """
        try:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event)
            return Response(serializer.data)
        except Event.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)


    def list(self, request):
        """Handle GET requests to get all events

        Returns:
            Response -- JSON serialized list of events
        """
        events = Event.objects.all()
        
        game = request.query_params.get('game', None)
        if game is not None:
            events = events.filter(game_id=game)
        
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)



    ########################
    ######## UPDATE ########
    ########################
    
    def update(self, request, pk):
        """Handle PUT requests for a event

        Returns:
            Response -- Empty body with 204 status code
        """

        event = Event.objects.get(pk=pk)
        event.description = request.data["description"]
        event.date = request.data["date"]
        event.time = request.data["time"]
        
        organizer = Gamer.objects.get(id=request.data["organizer"])
        event.organizer = organizer
        game = Game.objects.get(pk=request.data["game"])
        event.game = game
        
        event.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)



    ########################
    ######## DELETE ########
    ########################
    
    def destroy(self, request, pk):
        event = Event.objects.get(pk=pk)
        event.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    
    ########################
    ######## CUSTOM ########
    ######## ACTION ########
    ########################
    
    # Using the action decorator turns a method into a new route. In this case, the action will accept POST methods and because detail=True the url will include the pk. Since we need to know which event the user wants to sign up for we’ll need to have the pk. The route is named after the function. So to call this method the url would be http://localhost:8000/events/2/signup

    # Just like in the create method, we get the gamer that’s logged in, then the event by it’s pk. Since this is stored in the EventGamer table, we need to use the ORM to create a row on that table. This table will store the gamer_id of the user being added to the game (who's game_id is stored on the row as well). The response then sends back a 201 status code.
    
    @action(methods=['post'], detail=True)
    def signup(self, request, pk):
        """Post request for a user to sign up for an event"""

        gamer = Gamer.objects.get(uid=request.data["userId"])
        event = Event.objects.get(pk=pk)
        attendee = EventGamer.objects.create(
            gamer=gamer,
            event=event
        )
        return Response({'message': 'Gamer added'}, status=status.HTTP_201_CREATED)
    
    @action(methods=['delete'], detail=True)
    def leave(self, request, pk):
        """Delete request for a user to un-sign up for an event"""

        gamer = Gamer.objects.get(uid=request.data["userId"])
        event = Event.objects.get(pk=pk)
        attendee = EventGamer.objects.get(
            gamer=gamer,
            event=event
        )
        attendee.delete()
        return Response({'message': 'Gamer deleted'}, status=status.HTTP_204_NO_CONTENT)


class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for events
    """
    class Meta:
        model = Event
        fields = ('id', 'game', 'description', 'date', 'time', 'organizer')
        depth = 1
