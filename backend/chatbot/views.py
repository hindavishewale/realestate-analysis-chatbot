from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from .utils import RealEstateAnalyzer
import re
import pandas as pd
from io import BytesIO

# Create analyzer instance
analyzer = RealEstateAnalyzer()

@api_view(['POST'])
def analyze_query(request):
    try:
        query = request.data.get('query', '').lower()
        print(f"📨 Received query: {query}")
        
        if not query:
            return Response({'error': 'Query cannot be empty'}, status=400)
        
        # Handle comparison queries
        if 'compare' in query:
            areas = extract_multiple_areas(query)
            if len(areas) >= 2:
                print(f"🔄 Comparing areas: {areas[0]} and {areas[1]}")
                
                # Analyze both areas
                area1_result = analyzer.analyze_area(areas[0])
                area2_result = analyzer.analyze_area(areas[1])
                
                if area1_result and area2_result:
                    comparison_result = {
                        'area1': area1_result,
                        'area2': area2_result,
                        'comparison_summary': f"Comparison between {areas[0]} and {areas[1]}"
                    }
                    return Response(comparison_result)
                else:
                    return Response({'error': f'Could not compare {areas[0]} and {areas[1]}'})
            else:
                return Response({'error': 'Please specify two areas to compare. Example: "Compare Wakad and Aundh"'})
        
        # Handle price growth queries
        elif 'price growth' in query or 'price trend' in query:
            area = extract_single_area_from_query(query)
            if area:
                print(f"💰 Analyzing price growth for: {area}")
                result = analyzer.analyze_area(area)
                if result:
                    # Add price growth specific summary
                    price_growth_info = calculate_price_growth(result['table_data'])
                    result['summary'] += f"\n\n💰 Price Growth Analysis:\n{price_growth_info}"
                    return Response(result)
                else:
                    return Response({'error': f'No data found for {area}'}, status=404)
            else:
                return Response({'error': 'Please specify an area for price analysis. Example: "Show price growth for Aundh"'})
        
        # Handle single area analysis (analyze, analysis, or any other query)
        else:
            area = extract_single_area_from_query(query)
            if area:
                print(f"🔍 Analyzing single area: {area}")
                result = analyzer.analyze_area(area)
                if result:
                    return Response(result)
                else:
                    return Response({'error': f'No data found for {area}'}, status=404)
            else:
                # Default to Wakad if no area specified
                print("🔍 No area specified, defaulting to Wakad")
                result = analyzer.analyze_area('Wakad')
                if result:
                    return Response(result)
                else:
                    return Response({'error': 'Please specify an area to analyze. Example: "Analyze Wakad"'})
    
    except Exception as e:
        print(f"❌ Error in analyze_query: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return Response({'error': f'Internal server error: {str(e)}'}, status=500)

@api_view(['POST'])
def download_data(request):
    """Download filtered data as Excel or CSV"""
    try:
        query = request.data.get('query', '').lower()
        format_type = request.data.get('format', 'excel')  # excel or csv
        
        print(f"📥 Download request: {query} as {format_type}")
        
        if not query:
            return Response({'error': 'Query cannot be empty'}, status=400)
        
        # Use the same analysis logic to get filtered data
        if 'compare' in query:
            # Handle comparison download
            areas = extract_multiple_areas(query)
            if len(areas) >= 2:
                area1_data = analyzer.analyze_area(areas[0])
                area2_data = analyzer.analyze_area(areas[1])
                
                if area1_data and area2_data:
                    # Combine both areas' data
                    combined_data = area1_data['table_data'] + area2_data['table_data']
                    filename = f"comparison_{areas[0]}_vs_{areas[1]}"
                else:
                    return Response({'error': 'Could not get data for download'}, status=400)
            else:
                return Response({'error': 'Please specify two areas to compare'}, status=400)
        else:
            # Handle single area download
            area = extract_single_area_from_query(query)
            if area:
                result = analyzer.analyze_area(area)
                if result:
                    combined_data = result['table_data']
                    filename = f"analysis_{area}"
                else:
                    return Response({'error': f'No data found for {area}'}, status=404)
            else:
                return Response({'error': 'Please specify an area to analyze'}, status=400)
        
        # Convert to DataFrame
        df = pd.DataFrame(combined_data)
        
        # Create download file
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
            df.to_csv(response, index=False)
        else:  # excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Real Estate Data', index=False)
                # Auto-adjust column widths
                worksheet = writer.sheets['Real Estate Data']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = (max_length + 2)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
        
        print(f"✅ Download prepared: {len(combined_data)} records as {format_type}")
        return response
        
    except Exception as e:
        print(f"❌ Error in download_data: {str(e)}")
        return Response({'error': f'Download failed: {str(e)}'}, status=500)

@api_view(['GET'])
def download_sample_data(request):
    """Download sample dataset template"""
    try:
        # Create sample data structure
        sample_data = {
            'year': [2020, 2021, 2022, 2023],
            'area': ['Sample Area', 'Sample Area', 'Sample Area', 'Sample Area'],
            'price': [500000, 550000, 600000, 650000],
            'demand': [75, 80, 85, 82],
            'size': [1000, 1100, 1200, 1250],
            'description': ['Sample data for reference', 'Sample data for reference', 
                          'Sample data for reference', 'Sample data for reference']
        }
        
        df = pd.DataFrame(sample_data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sample Data', index=False)
            
            # Add a guide sheet
            guide_data = {
                'Column Name': ['area', 'year', 'price', 'demand', 'size'],
                'Description': [
                    'Name of the locality/area',
                    'Year of data (2020, 2021, etc.)',
                    'Property price in INR',
                    'Demand percentage (0-100)',
                    'Property size in sqft'
                ],
                'Example': [
                    'Wakad, Aundh, Akurdi',
                    '2023',
                    '650000',
                    '82',
                    '1250'
                ]
            }
            guide_df = pd.DataFrame(guide_data)
            guide_df.to_excel(writer, sheet_name='Data Guide', index=False)
        
        response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="real_estate_data_template.xlsx"'
        
        return response
        
    except Exception as e:
        print(f"❌ Error in download_sample_data: {str(e)}")
        return Response({'error': 'Sample download failed'}, status=500)

def extract_single_area_from_query(query):
    """Extract area name from query for single analysis"""
    # Remove common query words
    query = query.replace('analyze', '').replace('analysis', '').replace('show', '').replace('price', '').replace('growth', '').replace('trend', '').replace('for', '').replace('me', '').replace('give', '')
    
    words = query.split()
    stop_words = ['of', 'the', 'a', 'an', 'last', 'years', 'year', 'demand']
    area_words = [word for word in words if word.lower() not in stop_words and not word.isdigit() and word.strip()]
    
    area = ' '.join(area_words).title() if area_words else None
    
    # If still no area found, try to extract any capitalized word
    if not area:
        words = query.split()
        capitalized_words = [word for word in words if word[0].isupper() if word]
        if capitalized_words:
            area = ' '.join(capitalized_words)
    
    print(f"🔍 Extracted area: {area}")
    return area

def extract_multiple_areas(query):
    """Extract multiple areas from comparison query"""
    # Remove the word 'compare' and split by 'and' or commas
    query = query.replace('compare', '').strip()
    
    # Split by 'and' or commas
    if ' and ' in query:
        areas = [area.strip() for area in query.split(' and ')]
    elif ',' in query:
        areas = [area.strip() for area in query.split(',')]
    else:
        # If no separator, try to split by spaces (take first two words as areas)
        words = query.split()
        areas = words[:2] if len(words) >= 2 else words
    
    # Clean up and title case
    areas = [area.strip().title() for area in areas if area.strip()]
    
    print(f"🔍 Extracted areas: {areas}")
    return areas

def calculate_price_growth(table_data):
    """Calculate detailed price growth information"""
    if not table_data or len(table_data) < 2:
        return "Insufficient data for price growth analysis"
    
    # Sort by year
    sorted_data = sorted(table_data, key=lambda x: x['year'])
    
    first_year = sorted_data[0]['year']
    last_year = sorted_data[-1]['year']
    first_price = sorted_data[0]['price']
    last_price = sorted_data[-1]['price']
    
    total_growth = last_price - first_price
    growth_percentage = (total_growth / first_price) * 100
    
    # Calculate annual growth
    years_diff = last_year - first_year
    annual_growth = total_growth / years_diff if years_diff > 0 else 0
    annual_growth_percentage = growth_percentage / years_diff if years_diff > 0 else 0
    
    analysis = f"""
- Period: {first_year} to {last_year} ({years_diff} years)
- Starting Price: ₹{first_price:,.2f}
- Ending Price: ₹{last_price:,.2f}
- Total Growth: ₹{total_growth:,.2f} ({growth_percentage:.1f}%)
- Annual Growth: ₹{annual_growth:,.2f} per year ({annual_growth_percentage:.1f}% per year)
"""
    
    # Add growth trend
    if growth_percentage > 20:
        trend = "🚀 Strong growth"
    elif growth_percentage > 10:
        trend = "📈 Moderate growth"
    elif growth_percentage > 0:
        trend = "↗️ Slow growth"
    else:
        trend = "↘️ Price decline"
    
    analysis += f"- Market Trend: {trend}"
    
    return analysis