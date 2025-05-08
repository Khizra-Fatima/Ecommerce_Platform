from rest_framework import serializers
from .models import Product, Category, Size, WeightUnit, DimensionUnit, Tag, Color, Material




class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'

class WeightUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightUnit
        fields = '__all__'

class DimensionUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimensionUnit
        fields = '__all__'


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'





class ProductSerializer(serializers.ModelSerializer):
    colors = serializers.PrimaryKeyRelatedField(queryset=Color.objects.all(), many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    materials = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all(), many=True)

    def validate(self, data):
        if self.context['request'].method == 'POST' and not data.get('tags'):
            raise serializers.ValidationError({"tags": "At least one tag is required."})
        return data


    class Meta:
        model = Product
        fields = '__all__'

        