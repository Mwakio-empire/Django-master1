# shop/recommendations.py
from .models import Purchase, Recommendation, Product
from django.contrib.auth.models import User

def update_recommendations(user):
    purchases = Purchase.objects.filter(user=user)
    product_ids = [purchase.product.id for purchase in purchases]
    all_purchases = Purchase.objects.exclude(user=user).filter(product__in=product_ids)
    
    recommendations = {}
    for purchase in all_purchases:
        if purchase.product.id not in recommendations:
            recommendations[purchase.product.id] = 0
        recommendations[purchase.product.id] += 1

    for product_id, score in recommendations.items():
        Recommendation.objects.create(user=user, product_id=product_id, score=score)
