from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import RealEstateAnalyzer
import re

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