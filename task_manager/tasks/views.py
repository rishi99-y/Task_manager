from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from .models import Task
from .serializers import TaskSerializer, TaskCreateUpdateSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def task_list_create(request):
    """List all tasks for user or create a new task"""
    if request.method == 'GET':
        try:
            tasks = Task.objects.filter(user=request.user)
            
            # Filter by status if provided
            status_filter = request.query_params.get('status')
            if status_filter:
                tasks = tasks.filter(status=status_filter)
            
            # Filter by priority if provided
            priority_filter = request.query_params.get('priority')
            if priority_filter:
                tasks = tasks.filter(priority=priority_filter)
            
            # Pagination
            page = request.query_params.get('page', 1)
            paginator = Paginator(tasks, 10)
            page_obj = paginator.get_page(page)
            
            serializer = TaskSerializer(page_obj, many=True)
            return Response({
                'tasks': serializer.data,
                'total_pages': paginator.num_pages,
                'current_page': int(page),
                'total_tasks': paginator.count
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    elif request.method == 'POST':
        try:
            serializer = TaskCreateUpdateSerializer(data=request.data)
            if serializer.is_valid():
                task = serializer.save(user=request.user)
                return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def task_detail(request, pk):
    """Retrieve, update or delete a task"""
    try:
        task = get_object_or_404(Task, pk=pk, user=request.user)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        try:
            serializer = TaskSerializer(task)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    elif request.method == 'PUT':
        try:
            serializer = TaskCreateUpdateSerializer(task, data=request.data)
            if serializer.is_valid():
                task = serializer.save()
                return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    elif request.method == 'DELETE':
        try:
            task.delete()
            return Response({'message': 'Task deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_stats(request):
    """Get task statistics for the user"""
    try:
        user_tasks = Task.objects.filter(user=request.user)
        stats = {
            'total_tasks': user_tasks.count(),
            'pending_tasks': user_tasks.filter(status='pending').count(),
            'in_progress_tasks': user_tasks.filter(status='in_progress').count(),
            'completed_tasks': user_tasks.filter(status='completed').count(),
            'high_priority_tasks': user_tasks.filter(priority='high').count(),
            'medium_priority_tasks': user_tasks.filter(priority='medium').count(),
            'low_priority_tasks': user_tasks.filter(priority='low').count(),
        }
        return Response(stats, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)