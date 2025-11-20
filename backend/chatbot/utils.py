import pandas as pd
import os
from django.conf import settings
import requests

class RealEstateAnalyzer:
    def __init__(self, file_path=None):
        if file_path is None:
            file_path = os.path.join(settings.BASE_DIR, 'real_estate_data.xlsx')
        self.file_path = file_path
        self.df = self.load_data()
    
    def load_data(self):
        """Load and process the REAL Excel data"""
        try:
            print(f"📂 Loading real Excel data from: {self.file_path}")
            
            # Load the Excel file
            df = pd.read_excel(self.file_path)
            print(f"✅ SUCCESS! Loaded REAL Excel data with {len(df)} rows and {len(df.columns)} columns")
            
            # Process the real data
            df = self.process_real_data(df)
            
            print(f"🎯 Final processed data: {df.shape}")
            print(f"📍 Available areas: {list(df['area'].unique())}")
            print(f"📅 Years available: {sorted(df['year'].unique())}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error loading real Excel data: {e}")
            print("🔄 Falling back to sample data...")
            return self.create_sample_data()
    
    def process_real_data(self, df):
        """Process the real Excel data with proper column mapping"""
        print("🔄 Processing real Excel data columns...")
        
        # Map the actual columns from your Excel file
        column_mapping = {
            'final location': 'area',           # This is the area/locality
            'year': 'year',                     # Year column
            'flat - weighted average rate': 'price',  # Use flat rate as price
            'total_sales - igr': 'demand',      # Use total sales as demand indicator
            'total carpet area supplied (sqft)': 'size'  # Use carpet area as size
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        print(f"🔧 Column mapping applied: {column_mapping}")
        
        # Ensure we have the required columns, add defaults if missing
        required_columns = ['area', 'year', 'price', 'demand', 'size']
        for col in required_columns:
            if col not in df.columns:
                if col == 'price':
                    # Try alternative price columns
                    price_columns = [c for c in df.columns if 'rate' in str(c).lower() or 'price' in str(c).lower()]
                    if price_columns:
                        df['price'] = df[price_columns[0]]
                        print(f"🔧 Using alternative price column: {price_columns[0]}")
                    else:
                        df['price'] = 500000  # Default price
                elif col == 'demand':
                    # Try alternative demand columns
                    demand_columns = [c for c in df.columns if 'sold' in str(c).lower() or 'sales' in str(c).lower()]
                    if demand_columns:
                        df['demand'] = df[demand_columns[0]]
                        print(f"🔧 Using alternative demand column: {demand_columns[0]}")
                    else:
                        df['demand'] = 75  # Default demand
                elif col == 'size':
                    df['size'] = 1000  # Default size
                else:
                    print(f"⚠️ Missing required column: {col}")
        
        # Clean the data
        df = self.clean_data(df)
        
        print("✅ Real Excel data processing complete!")
        return df
    
    def clean_data(self, df):
        """Clean and prepare the data for analysis"""
        print("🧹 Cleaning data...")
        
        # Remove rows with missing critical data
        initial_count = len(df)
        df = df.dropna(subset=['area', 'year'])
        print(f"📊 Removed {initial_count - len(df)} rows with missing area/year")
        
        # Ensure correct data types
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['demand'] = pd.to_numeric(df['demand'], errors='coerce')
        df['size'] = pd.to_numeric(df['size'], errors='coerce')
        
        # Remove invalid rows
        df = df.dropna(subset=['year'])
        
        # Fill missing values with reasonable defaults
        if 'price' in df.columns:
            df['price'] = df['price'].fillna(df['price'].median())
        if 'demand' in df.columns:
            df['demand'] = df['demand'].fillna(df['demand'].median())
        if 'size' in df.columns:
            df['size'] = df['size'].fillna(1000)
        
        # Standardize area names
        df['area'] = df['area'].astype(str).str.title().str.strip()
        
        # Normalize demand to percentage scale (0-100) if needed
        if 'demand' in df.columns:
            max_demand = df['demand'].max()
            if max_demand > 100:  # If demand values are large, normalize to percentage
                df['demand'] = (df['demand'] / max_demand) * 100
                print("📈 Normalized demand values to percentage scale")
        
        print(f"✅ Data cleaning complete. Final dataset: {df.shape}")
        return df
    
    def create_sample_data(self):
        """Create sample data only if real data fails"""
        print("📝 Generating sample data as fallback...")
        sample_data = {
            'year': [2020, 2021, 2022, 2023, 2020, 2021, 2022, 2023, 2020, 2021, 2022, 2023],
            'area': ['Wakad', 'Wakad', 'Wakad', 'Wakad', 
                    'Aundh', 'Aundh', 'Aundh', 'Aundh',
                    'Akurdi', 'Akurdi', 'Akurdi', 'Akurdi'],
            'price': [500000, 550000, 600000, 650000, 
                     600000, 650000, 700000, 750000,
                     450000, 480000, 520000, 560000],
            'demand': [75, 80, 85, 82, 
                       70, 75, 80, 78,
                       65, 70, 75, 77],
            'size': [1000, 1100, 1200, 1250, 
                     1100, 1150, 1200, 1250,
                     950, 1000, 1050, 1100]
        }
        return pd.DataFrame(sample_data)
    
    def analyze_area(self, area_name):
        """Analyze data for specific area using REAL Excel data"""
        print(f"🔍 Analyzing area: {area_name}")
        
        # Check if we have real data
        is_real_data = len(self.df) > 10 and 'area' in self.df.columns
        
        if not is_real_data or self.df.empty:
            print("❌ No valid real data available")
            return self.generate_sample_analysis(area_name)
        
        # Get available areas
        available_areas = self.df['area'].unique()
        print(f"📍 Available REAL areas: {list(available_areas)}")
        
        # Case-insensitive area matching
        area_pattern = area_name.lower()
        matching_areas = [area for area in available_areas if area_pattern in area.lower()]
        
        if matching_areas:
            # Use the first matching area
            matched_area = matching_areas[0]
            print(f"🎯 Matched '{area_name}' to REAL area: '{matched_area}'")
            area_data = self.df[self.df['area'].str.lower() == matched_area.lower()]
        else:
            print(f"⚠️ No match found for '{area_name}' in real data")
            return self.generate_sample_analysis(area_name)
        
        if area_data.empty:
            print(f"❌ No data found for matched area '{matched_area}'")
            return self.generate_sample_analysis(area_name)
        
        print(f"✅ Found {len(area_data)} REAL records for {matched_area}")
        
        # Generate analysis
        summary = self.generate_summary(area_data, matched_area, is_real_data=True)
        chart_data = self.prepare_chart_data(area_data)
        table_data = area_data[['year', 'area', 'price', 'demand', 'size']].to_dict('records')
        
        return {
            'summary': summary,
            'chart_data': chart_data,
            'table_data': table_data,
            'area': matched_area,
            'data_source': 'Real Excel Data'
        }
    
    def generate_sample_analysis(self, area_name):
        """Generate sample analysis for areas not in real data"""
        print(f"🔄 Generating sample analysis for {area_name}")
        sample_data = self.create_sample_data()
        area_sample = sample_data[sample_data['area'] == area_name]
        
        if area_sample.empty:
            # Create data for this area
            area_sample = pd.DataFrame({
                'year': [2020, 2021, 2022, 2023],
                'area': [area_name, area_name, area_name, area_name],
                'price': [500000, 550000, 600000, 650000],
                'demand': [75, 80, 85, 82],
                'size': [1000, 1100, 1200, 1250]
            })
        
        summary = self.generate_summary(area_sample, area_name, is_real_data=False)
        chart_data = self.prepare_chart_data(area_sample)
        table_data = area_sample.to_dict('records')
        
        return {
            'summary': summary,
            'chart_data': chart_data,
            'table_data': table_data,
            'area': area_name,
            'data_source': 'Sample Data'
        }
    
    def generate_summary(self, data, area_name, is_real_data=True):
        """Generate comprehensive text summary"""
        try:
            # Sort by year
            data = data.sort_values('year')
            
            # Calculate metrics
            avg_price = data['price'].mean()
            avg_demand = data['demand'].mean() if 'demand' in data.columns else 0
            latest_year = data['year'].max()
            price_growth = self.calculate_price_growth(data)
            
            # Generate insights based on real vs sample data
            if is_real_data:
                data_source_note = "📊 **Real Market Data Analysis**"
                credibility = "Based on actual real estate market data"
            else:
                data_source_note = "📝 **Sample Data Analysis**"
                credibility = "Based on sample data for demonstration"
            
            price_trend = "significant growth" if price_growth > 15 else "moderate growth" if price_growth > 5 else "stable"
            demand_level = "high" if avg_demand > 80 else "moderate" if avg_demand > 60 else "low"
            
            summary = f"""
🏠 Real Estate Analysis for {area_name}

{data_source_note}
{credibility}

📊 Key Metrics:
• Average Price: ₹{avg_price:,.2f}
• Average Demand: {avg_demand:.1f}%
• Latest Data Year: {latest_year}
• Records Analyzed: {len(data)}
• Price Growth: {price_growth:.1f}% over period

📈 Market Insights:
• Price trend shows {price_trend}
• Demand is {demand_level} in this area
• Market appears {'appreciating' if price_growth > 10 else 'stable'}

💡 Recommendation:
This area shows {'strong investment potential' if price_growth > 15 and avg_demand > 70 else 'moderate potential' if price_growth > 5 else 'stable performance'}.
"""
            return summary.strip()
            
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
            return f"Analysis for {area_name}\n- Real Excel data processed\n- Detailed analysis available"
    
    def calculate_price_growth(self, data):
        """Calculate price growth percentage"""
        if len(data) < 2:
            return 0
        
        sorted_data = data.sort_values('year')
        first_price = sorted_data['price'].iloc[0]
        last_price = sorted_data['price'].iloc[-1]
        
        return ((last_price - first_price) / first_price) * 100
    
    def prepare_chart_data(self, data):
        """Prepare data for charts"""
        try:
            data = data.sort_values('year')
            
            chart_data = {
                'price_trend': {
                    'labels': data['year'].tolist(),
                    'data': data['price'].tolist()
                },
                'demand_trend': {
                    'labels': data['year'].tolist(),
                    'data': data['demand'].tolist() if 'demand' in data.columns else [70, 75, 80, 78]
                }
            }
            return chart_data
            
        except Exception as e:
            print(f"❌ Error preparing chart data: {e}")
            return {
                'price_trend': {'labels': [2020, 2021, 2022, 2023], 'data': [500000, 550000, 600000, 650000]},
                'demand_trend': {'labels': [2020, 2021, 2022, 2023], 'data': [75, 80, 85, 82]}
            }
    
    def compare_areas(self, area1, area2):
        """Compare two areas"""
        area1_result = self.analyze_area(area1)
        area2_result = self.analyze_area(area2)
        
        if not area1_result or not area2_result:
            return None
        
        return {
            'area1': area1_result,
            'area2': area2_result,
            'comparison_summary': f"Comparison between {area1} and {area2}"
        }