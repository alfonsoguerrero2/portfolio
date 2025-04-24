from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Portfolio
from datetime import datetime, timedelta
from decimal import Decimal
from rest_framework import status


@api_view(['GET'])
@permission_classes([AllowAny])
def portfolio_summary(request):
    # Parse query parameters
    try:
        initial_date = datetime.strptime(request.GET.get('initial_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return Response({'error': 'Provide initial_date and end_date in YYYY-MM-DD format.'}, status=400)

    
    try:
        p1 = Portfolio.objects.get(pk=1)
        p2 = Portfolio.objects.get(pk=2)
    except Portfolio.DoesNotExist:
        return Response({'error': 'Portfolio 1 or 2 does not exist.'}, status=404)

    
    data = []
    current = initial_date
    while current <= end_date:
        p1_value = p1.total_value(current)
        p2_value = p2.total_value(current)

        p1_weights = p1.asset_weights(current)
        p2_weights = p2.asset_weights(current)

        data.append({
            'date': current.isoformat(),
            'portfolio_1': {
                'total_value': float(p1_value),
                'weights': {k: float(v) for k, v in p1_weights.items()}
            },
            'portfolio_2': {
                'total_value': float(p2_value),
                'weights': {k: float(v) for k, v in p2_weights.items()}
            }
        })
        current += timedelta(days=1)

    return Response(data, status=status.HTTP_200_OK)
