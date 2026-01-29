from django.db import models

# Create your models here.

class Category(models.Model):
    CategoryName = models.CharField(max_length=255)
    CategoryDescription = models.TextField()
    CreationDate = models.DateTimeField(auto_now_add=True)
    UpdationDate = models.DateTimeField(auto_now_add=True)

class Product(models.Model):
    CategoryId = models.ForeignKey(Category,on_delete=models.CASCADE)
    ProductName = models.CharField(max_length=255)
    ProductPrice = models.FloatField()
    ProductDiscountPrice = models.FloatField()
    ShortDescription = models.TextField()
    LongDescription = models.TextField()
    ProductImage1 = models.ImageField(upload_to='products/products/')
    ProductImage2 = models.ImageField(upload_to='products/products/')
    ProductImage3 = models.ImageField(upload_to='products/products/')
    ProductFile = models.FileField(upload_to='products/productsFile/')
    CreationDate = models.DateTimeField(auto_now_add=True)
    UpdationDate = models.DateTimeField(auto_now_add=True)