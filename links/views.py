from datetime import timedelta
import hashlib, io
import qrcode

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.db import models
from django.db.models import Count
from django.db.models.functions import TruncDate

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter

from django.contrib.auth import get_user_model
from .models import Link, Click
from .serializers import RegisterSerializer, LinkSerializer

User = get_user_model()

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(request=RegisterSerializer, responses={201: None})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Đăng ký thành công!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LinksListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='q', description='Tìm theo title (icontains)', required=False, type=str),
            OpenApiParameter(name='owner', description='Lọc theo owner id (admin mới có hiệu lực)', required=False, type=int),
            OpenApiParameter(name='created_at', description='Lọc theo ngày tạo YYYY-MM-DD', required=False, type=str),
            OpenApiParameter(name='page', description='Trang (phân trang)', required=False, type=int),
        ],
        responses=LinkSerializer
    )
    def get(self, request):
        qs = Link.objects.all().select_related('owner')
        if not request.user.is_staff:
            qs = qs.filter(owner=request.user)
        q = request.query_params.get('q')
        if q:
            qs = qs.filter(title__icontains=q)
        owner = request.query_params.get('owner')
        if owner and request.user.is_staff:
            qs = qs.filter(owner_id=owner)
        created_at = request.query_params.get('created_at')
        if created_at:
            qs = qs.filter(created_at__date=created_at)

        qs = qs.order_by('-created_at')
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        ser = LinkSerializer(page, many=True)
        return paginator.get_paginated_response(ser.data)

    @extend_schema(request=LinkSerializer, responses=LinkSerializer)
    def post(self, request):
        serializer = LinkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LinkDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, request, pk):
        try:
            obj = Link.objects.select_related('owner').get(pk=pk)
        except Link.DoesNotExist:
            raise Http404
        if not request.user.is_staff and obj.owner != request.user:
            raise Http404
        return obj

    @extend_schema(responses=LinkSerializer)
    def get(self, request, pk):
        obj = self._get(request, pk)
        return Response(LinkSerializer(obj).data)

    @extend_schema(request=LinkSerializer, responses=LinkSerializer)
    def patch(self, request, pk):
        obj = self._get(request, pk)
        serializer = LinkSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self._get(request, pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class LinkStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(parameters=[OpenApiParameter(name='range', description='7d | 30d', required=False, type=str)])
    def get(self, request, pk):
        try:
            link = Link.objects.get(pk=pk)
        except Link.DoesNotExist:
            raise Http404
        if not request.user.is_staff and link.owner != request.user:
            raise Http404

        range_param = request.query_params.get('range', '7d')
        days = 30 if range_param == '30d' else 7
        cutoff = timezone.now() - timedelta(days=days)

        clicks_qs = link.clicks.filter(ts__gte=cutoff)
        total = clicks_qs.count()
        daily_clicks = (clicks_qs
                        .annotate(day=TruncDate('ts'))
                        .values('day')
                        .annotate(count=models.Count('id'))
                        .order_by('day'))
        data = [{"date": d['day'].strftime("%Y-%m-%d"), "count": d['count']} for d in daily_clicks]
        return Response({"range": f"{days}d", "total_clicks": total, "daily_clicks": data})

class TopLinksAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(parameters=[OpenApiParameter(name='limit', description='Số link', required=False, type=int)])
    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        top_links = (Link.objects
                     .annotate(click_count=Count('clicks'))
                     .order_by('-click_count')[:limit])
        data = [{
            "id": l.id,
            "title": l.title,
            "slug": l.slug,
            "owner": l.owner.username,
            "click_count": l.click_count or 0
        } for l in top_links]
        return Response(data)

class LinkQRAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            link = Link.objects.get(pk=pk)
        except Link.DoesNotExist:
            raise Http404
        if not request.user.is_staff and link.owner != request.user:
            raise Http404
        short = request.build_absolute_uri(f'/r/{link.slug}/')
        img = qrcode.make(short)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return HttpResponse(buf.getvalue(), content_type='image/png')

class RedirectAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def get(self, request, slug):
        try:
            link = Link.objects.get(slug=slug, is_active=True)
        except Link.DoesNotExist:
            raise Http404
        xff = (request.META.get('HTTP_X_FORWARDED_FOR') or '').split(',')[0].strip()
        ip = xff or request.META.get('REMOTE_ADDR', '') or ''
        from django.conf import settings
        ip_hash = hashlib.sha256((ip + getattr(settings, 'SECRET_KEY', 'secret')).encode()).hexdigest()
        Click.objects.create(
            link=link,
            referrer=request.META.get('HTTP_REFERER', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            ip_hash=ip_hash,
        )
        return HttpResponseRedirect(link.target_url)
