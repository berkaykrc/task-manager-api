# serializers.py
from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    tasks = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='task-detail'
    )

    class Meta:
        model = Profile
        fields = ['user', 'image']
