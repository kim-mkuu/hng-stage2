from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse
from django.db.models import Q
from django.conf import settings
from .models import Country
from .serializers import CountrySerializer, StatusSerializer
from .utils import fetch_countries, fetch_exchange_rates, calculate_estimated_gdp, generate_summary_image
import os


#views creation

@api_view(['POST'])
def refresh_countries(request):
    """Fetch and cache country data from external APIs"""
    try:
        # Fetch data from external APIs
        countries_data = fetch_countries()
        exchange_rates = fetch_exchange_rates()
        
        # Process each country
        for country_data in countries_data:
            try:
                name = country_data.get('name')
                population = country_data.get('population')
                
                # Skip if required fields are missing
                if not name or population is None:
                    continue
                
                capital = country_data.get('capital')
                region = country_data.get('region')
                flag_url = country_data.get('flag')
                currencies = country_data.get('currencies', [])
                
                # Handle currency
                currency_code = None
                exchange_rate = None
                estimated_gdp = None
                
                if currencies and len(currencies) > 0:
                    currency_code = currencies[0].get('code')
                    
                    if currency_code and currency_code in exchange_rates:
                        exchange_rate = exchange_rates[currency_code]
                        estimated_gdp = calculate_estimated_gdp(population, exchange_rate)
                
                # Set estimated_gdp to 0 if no currency
                if not currency_code:
                    estimated_gdp = 0
                
                # Update or create country
                Country.objects.update_or_create(
                    name__iexact=name,
                    defaults={
                        'name': name,
                        'capital': capital,
                        'region': region,
                        'population': population,
                        'currency_code': currency_code,
                        'exchange_rate': exchange_rate,
                        'estimated_gdp': estimated_gdp,
                        'flag_url': flag_url,
                    }
                )
            except Exception as e:
                # Continue processing other countries if one fails
                continue
        
        # Generate summary image
        total_countries = Country.objects.count()
        top_countries = Country.objects.filter(estimated_gdp__isnull=False).order_by('-estimated_gdp')[:5]
        last_refresh = Country.objects.first().last_refreshed_at if Country.objects.exists() else None
        
        generate_summary_image(total_countries, top_countries, last_refresh)
        
        return Response({
            "message": "Countries refreshed successfully",
            "total_countries": total_countries
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        error_message = str(e)
        api_name = "restcountries.com" if "restcountries" in error_message else "open.er-api.com"
        return Response({
            "error": "External data source unavailable",
            "details": f"Could not fetch data from {api_name}"
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

@api_view(['GET'])
def list_countries(request):
    """Get all countries with optional filters and sorting"""
    countries = Country.objects.all()
    
    # Filter by region
    region = request.query_params.get('region')
    if region:
        countries = countries.filter(region__iexact=region)
    
    # Filter by currency
    currency = request.query_params.get('currency')
    if currency:
        countries = countries.filter(currency_code__iexact=currency)
    
    # Sort by GDP
    sort = request.query_params.get('sort')
    if sort == 'gdp_desc':
        countries = countries.order_by('-estimated_gdp')
    elif sort == 'gdp_asc':
        countries = countries.order_by('estimated_gdp')
    
    serializer = CountrySerializer(countries, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'DELETE'])
def country_detail(request, name):
    """Get or delete a country by name"""
    try:
        country = Country.objects.get(name__iexact=name)
        
        if request.method == 'GET':
            serializer = CountrySerializer(country)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'DELETE':
            country.delete()
            return Response({
                "message": f"Country '{name}' deleted successfully"
            }, status=status.HTTP_200_OK)
            
    except Country.DoesNotExist:
        return Response({
            "error": "Country not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "error": "Internal server error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_status(request):
    """Get total countries and last refresh timestamp"""
    total_countries = Country.objects.count()
    last_refreshed = Country.objects.first().last_refreshed_at if Country.objects.exists() else None
    
    data = {
        "total_countries": total_countries,
        "last_refreshed_at": last_refreshed
    }
    
    serializer = StatusSerializer(data)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_summary_image(request):
    """Serve the generated summary image"""
    image_path = os.path.join(settings.BASE_DIR, 'cache', 'summary.png')
    
    if os.path.exists(image_path):
        return FileResponse(open(image_path, 'rb'), content_type='image/png')
    else:
        return Response({
            "error": "Summary image not found"
        }, status=status.HTTP_404_NOT_FOUND)
