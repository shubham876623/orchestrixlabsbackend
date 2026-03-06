from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.throttling import AnonRateThrottle
from .models import Project
from .serializers import ProjectSerializer


class ProjectListView(ListAPIView):
    serializer_class = ProjectSerializer
    throttle_classes = []  # public read-only data, no throttling needed

    def get_queryset(self):
        qs = Project.objects.all()
        featured = self.request.query_params.get('featured')
        category = self.request.query_params.get('category')
        if featured is not None:
            qs = qs.filter(featured=True)
        if category:
            qs = qs.filter(category=category)
        return qs


class ProjectDetailView(RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    throttle_classes = []
