import React, { useState } from 'react';
import axios from 'axios';
import { Container, Row, Col, Form, Button, Card, Alert, Badge } from 'react-bootstrap';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Define TypeScript interfaces
interface ChartData {
  labels: number[];
  data: number[];
}

interface AnalysisResponse {
  summary: string;
  chart_data: {
    price_trend: ChartData;
    demand_trend: ChartData;
  };
  table_data: Array<{
    year: number;
    area: string;
    price: number;
    demand: number;
    size: number;
  }>;
  area: string;
  data_source?: string; // Add data source field
}

interface ComparisonResponse {
  area1: AnalysisResponse;
  area2: AnalysisResponse;
  comparison_summary: string;
}

type ApiResponse = AnalysisResponse | ComparisonResponse | { error: string };

// API configuration
const API_BASE_URL = 'http://127.0.0.1:8000';

function App() {
  const [query, setQuery] = useState('Analyze Wakad');
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    
    try {
      const result = await axios.post<ApiResponse>(`${API_BASE_URL}/api/analyze/`, {
        query: query
      }, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      console.log('API Response:', result.data);
      setResponse(result.data);
    } catch (err: any) {
      console.error('API Error:', err);
      if (err.code === 'ECONNREFUSED') {
        setError('Cannot connect to backend server. Make sure Django is running on port 8000.');
      } else if (err.response) {
        setError(`Backend error: ${err.response.status} - ${err.response.data?.error || 'Unknown error'}`);
      } else if (err.request) {
        setError('No response from server. Check if backend is running.');
      } else {
        setError('Something went wrong. Please try again.');
      }
      setResponse(null);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (format: 'excel' | 'csv' = 'excel') => {
    if (!query.trim()) {
      setError('Please enter a query before downloading');
      return;
    }

    try {
      console.log(`📥 Downloading data as ${format} for query: ${query}`);
      
      const response = await fetch(`${API_BASE_URL}/api/download/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          format: format
        }),
      });

      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
      }

      // Get the filename from content-disposition header or generate one
      const contentDisposition = response.headers.get('content-disposition');
      let filename = `real_estate_data.${format === 'excel' ? 'xlsx' : 'csv'}`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      console.log(`✅ Download successful: ${filename}`);
      
    } catch (err: any) {
      console.error('Download error:', err);
      setError(`Download failed: ${err.message}`);
    }
  };

  const handleDownloadSample = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/download-sample/`);
      
      if (!response.ok) {
        throw new Error('Sample download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'real_estate_data_template.xlsx';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      console.log('✅ Sample template downloaded');
      
    } catch (err: any) {
      console.error('Sample download error:', err);
      setError(`Sample download failed: ${err.message}`);
    }
  };

  // Type guards
  const isAnalysisResponse = (response: ApiResponse): response is AnalysisResponse => {
    return 'summary' in response && 'chart_data' in response;
  };

  const isComparisonResponse = (response: ApiResponse): response is ComparisonResponse => {
    return 'comparison_summary' in response && 'area1' in response && 'area2' in response;
  };

  const isErrorResponse = (response: ApiResponse): response is { error: string } => {
    return 'error' in response;
  };

  // Data source badge component
  const DataSourceBadge = ({ source }: { source?: string }) => {
    if (!source) return null;
    
    const getVariant = () => {
      switch (source) {
        case 'Real Excel Data': return 'success';
        case 'Sample Data': return 'warning';
        default: return 'secondary';
      }
    };

    return (
      <Badge bg={getVariant()} className="ms-2">
        📊 {source}
      </Badge>
    );
  };

  // Sample queries for quick testing
  const sampleQueries = [
    'Analyze Wakad',
    'Compare Wakad and Aundh',
    'Show price growth for Aundh',
    'Analyze Akurdi',
    'Compare Aundh and Akurdi'
  ];

  return (
    <Container className="my-4">
      <Row className="justify-content-center">
        <Col md={10}>
          <h1 className="text-center mb-4">🏠 Real Estate Analysis Chatbot</h1>
          
          {/* Connection Status */}
          <Alert variant="info" className="mb-4">
            <strong>Backend Status:</strong> ✅ Connected
            <br />
            <small>Backend running at: {API_BASE_URL}</small>
          </Alert>

          {/* Quick Query Buttons */}
          <Card className="mb-4">
            <Card.Body>
              <h6>Try these sample queries:</h6>
              <div className="d-flex flex-wrap gap-2">
                {sampleQueries.map((sampleQuery, index) => (
                  <Button
                    key={index}
                    variant="outline-primary"
                    size="sm"
                    onClick={() => setQuery(sampleQuery)}
                  >
                    {sampleQuery}
                  </Button>
                ))}
              </div>
            </Card.Body>
          </Card>

          {/* Query Input */}
          <Card className="shadow mb-4">
            <Card.Body>
              <Form onSubmit={handleSubmit}>
                <Form.Group>
                  <Form.Label>Enter your real estate query:</Form.Label>
                  <Form.Control
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g., Analyze Wakad, Compare Area1 and Area2, Show price growth for Area"
                    size="lg"
                  />
                </Form.Group>
                <Button 
                  variant="primary" 
                  type="submit" 
                  disabled={loading}
                  className="mt-3"
                  size="lg"
                >
                  {loading ? 'Analyzing...' : 'Analyze Real Estate Data'}
                </Button>

                {/* Download Options */}
                <div className="mt-3">
                  <h6>📥 Download Options:</h6>
                  <div className="d-flex flex-wrap gap-2">
                    <Button 
                      variant="success" 
                      onClick={() => handleDownload('excel')}
                      disabled={loading}
                      size="sm"
                    >
                      📊 Download Excel
                    </Button>
                    <Button 
                      variant="outline-success" 
                      onClick={() => handleDownload('csv')}
                      disabled={loading}
                      size="sm"
                    >
                      📄 Download CSV
                    </Button>
                    <Button 
                      variant="outline-info" 
                      onClick={handleDownloadSample}
                      size="sm"
                    >
                      📋 Get Template
                    </Button>
                  </div>
                  <small className="text-muted">
                    Download current analysis data or get a sample template
                  </small>
                </div>
              </Form>
            </Card.Body>
          </Card>

          {error && (
            <Alert variant="danger" className="mt-3">
              <strong>Error:</strong> {error}
            </Alert>
          )}

          {response && isErrorResponse(response) && (
            <Alert variant="warning" className="mt-3">
              <strong>Note:</strong> {response.error}
            </Alert>
          )}

          {/* Single Area Analysis */}
          {response && isAnalysisResponse(response) && (
            <div className="mt-4">
              <Card className="mb-4">
                <Card.Header className="bg-primary text-white">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">📊 Analysis for {response.area}</h5>
                    <DataSourceBadge source={response.data_source} />
                  </div>
                </Card.Header>
                <Card.Body>
                  <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', fontSize: '16px' }}>
                    {response.summary}
                  </pre>
                </Card.Body>
              </Card>

              {/* Charts */}
              <Row>
                <Col md={6}>
                  <Card className="mb-4">
                    <Card.Header>
                      <h6>💰 Price Trend (₹)</h6>
                    </Card.Header>
                    <Card.Body>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart 
                          data={response.chart_data.price_trend.labels.map((label: number, index: number) => ({
                            year: label,
                            price: response.chart_data.price_trend.data[index]
                          }))}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="year" />
                          <YAxis />
                          <Tooltip formatter={(value) => [`₹${Number(value).toLocaleString()}`, 'Price']} />
                          <Legend />
                          <Line 
                            type="monotone" 
                            dataKey="price" 
                            stroke="#8884d8" 
                            strokeWidth={2}
                            activeDot={{ r: 6 }} 
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </Card.Body>
                  </Card>
                </Col>
                
                <Col md={6}>
                  <Card className="mb-4">
                    <Card.Header>
                      <h6>📈 Demand Trend (%)</h6>
                    </Card.Header>
                    <Card.Body>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart 
                          data={response.chart_data.demand_trend.labels.map((label: number, index: number) => ({
                            year: label,
                            demand: response.chart_data.demand_trend.data[index]
                          }))}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="year" />
                          <YAxis />
                          <Tooltip formatter={(value) => [`${value}%`, 'Demand']} />
                          <Legend />
                          <Line 
                            type="monotone" 
                            dataKey="demand" 
                            stroke="#82ca9d" 
                            strokeWidth={2}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>

              {/* Data Table */}
              <Card>
                <Card.Header>
                  <div className="d-flex justify-content-between align-items-center">
                    <h6 className="mb-0">📋 Detailed Data Table</h6>
                    <DataSourceBadge source={response.data_source} />
                  </div>
                </Card.Header>
                <Card.Body>
                  <div className="table-responsive">
                    <table className="table table-striped table-hover">
                      <thead className="table-dark">
                        <tr>
                          <th>Year</th>
                          <th>Area</th>
                          <th>Price (₹)</th>
                          <th>Demand (%)</th>
                          <th>Size</th>
                        </tr>
                      </thead>
                      <tbody>
                        {response.table_data.map((row, index) => (
                          <tr key={index}>
                            <td>{row.year}</td>
                            <td><strong>{row.area}</strong></td>
                            <td>₹{row.price.toLocaleString()}</td>
                            <td>{row.demand}%</td>
                            <td>{row.size}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card.Body>
              </Card>

              {/* Export Section */}
              <Card className="mt-3">
                <Card.Body className="text-center">
                  <h6>💾 Export Analysis</h6>
                  <div className="d-flex justify-content-center gap-2">
                    <Button 
                      variant="success" 
                      onClick={() => handleDownload('excel')}
                      size="sm"
                    >
                      📊 Export to Excel
                    </Button>
                    <Button 
                      variant="outline-success" 
                      onClick={() => handleDownload('csv')}
                      size="sm"
                    >
                      📄 Export to CSV
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            </div>
          )}

          {/* Comparison Analysis */}
          {response && isComparisonResponse(response) && (
            <div className="mt-4">
              <Card className="mb-4 bg-light">
                <Card.Header className="bg-success text-white">
                  <h4>🔄 {response.comparison_summary}</h4>
                </Card.Header>
              </Card>
              
              <Row>
                {/* Area 1 */}
                <Col md={6}>
                  <Card className="mb-4">
                    <Card.Header className="bg-primary text-white">
                      <div className="d-flex justify-content-between align-items-center">
                        <h5 className="mb-0">📍 {response.area1.area}</h5>
                        <DataSourceBadge source={response.area1.data_source} />
                      </div>
                    </Card.Header>
                    <Card.Body>
                      <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', fontSize: '14px' }}>
                        {response.area1.summary}
                      </pre>
                      
                      {/* Area 1 Charts */}
                      <Row>
                        <Col md={12}>
                          <h6>💰 Price Trend</h6>
                          <ResponsiveContainer width="100%" height={200}>
                            <LineChart 
                              data={response.area1.chart_data.price_trend.labels.map((label: number, index: number) => ({
                                year: label,
                                price: response.area1.chart_data.price_trend.data[index]
                              }))}
                            >
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="year" />
                              <YAxis />
                              <Tooltip formatter={(value) => [`₹${Number(value).toLocaleString()}`, 'Price']} />
                              <Line type="monotone" dataKey="price" stroke="#8884d8" strokeWidth={2} />
                            </LineChart>
                          </ResponsiveContainer>
                        </Col>
                        <Col md={12}>
                          <h6>📈 Demand Trend</h6>
                          <ResponsiveContainer width="100%" height={200}>
                            <LineChart 
                              data={response.area1.chart_data.demand_trend.labels.map((label: number, index: number) => ({
                                year: label,
                                demand: response.area1.chart_data.demand_trend.data[index]
                              }))}
                            >
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="year" />
                              <YAxis />
                              <Tooltip formatter={(value) => [`${value}%`, 'Demand']} />
                              <Line type="monotone" dataKey="demand" stroke="#82ca9d" strokeWidth={2} />
                            </LineChart>
                          </ResponsiveContainer>
                        </Col>
                      </Row>
                    </Card.Body>
                  </Card>
                </Col>
                
                {/* Area 2 */}
                <Col md={6}>
                  <Card className="mb-4">
                    <Card.Header className="bg-warning text-dark">
                      <div className="d-flex justify-content-between align-items-center">
                        <h5 className="mb-0">📍 {response.area2.area}</h5>
                        <DataSourceBadge source={response.area2.data_source} />
                      </div>
                    </Card.Header>
                    <Card.Body>
                      <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', fontSize: '14px' }}>
                        {response.area2.summary}
                      </pre>
                      
                      {/* Area 2 Charts */}
                      <Row>
                        <Col md={12}>
                          <h6>💰 Price Trend</h6>
                          <ResponsiveContainer width="100%" height={200}>
                            <LineChart 
                              data={response.area2.chart_data.price_trend.labels.map((label: number, index: number) => ({
                                year: label,
                                price: response.area2.chart_data.price_trend.data[index]
                              }))}
                            >
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="year" />
                              <YAxis />
                              <Tooltip formatter={(value) => [`₹${Number(value).toLocaleString()}`, 'Price']} />
                              <Line type="monotone" dataKey="price" stroke="#ff7300" strokeWidth={2} />
                            </LineChart>
                          </ResponsiveContainer>
                        </Col>
                        <Col md={12}>
                          <h6>📈 Demand Trend</h6>
                          <ResponsiveContainer width="100%" height={200}>
                            <LineChart 
                              data={response.area2.chart_data.demand_trend.labels.map((label: number, index: number) => ({
                                year: label,
                                demand: response.area2.chart_data.demand_trend.data[index]
                              }))}
                            >
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="year" />
                              <YAxis />
                              <Tooltip formatter={(value) => [`${value}%`, 'Demand']} />
                              <Line type="monotone" dataKey="demand" stroke="#ff0040" strokeWidth={2} />
                            </LineChart>
                          </ResponsiveContainer>
                        </Col>
                      </Row>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>

              {/* Comparison Tables */}
              <Row>
                <Col md={6}>
                  <Card>
                    <Card.Header>
                      <div className="d-flex justify-content-between align-items-center">
                        <h6 className="mb-0">📋 {response.area1.area} Data</h6>
                        <DataSourceBadge source={response.area1.data_source} />
                      </div>
                    </Card.Header>
                    <Card.Body>
                      <div className="table-responsive">
                        <table className="table table-sm table-striped">
                          <thead>
                            <tr>
                              <th>Year</th>
                              <th>Price</th>
                              <th>Demand</th>
                              <th>Size</th>
                            </tr>
                          </thead>
                          <tbody>
                            {response.area1.table_data.map((row, index) => (
                              <tr key={index}>
                                <td>{row.year}</td>
                                <td>₹{row.price.toLocaleString()}</td>
                                <td>{row.demand}%</td>
                                <td>{row.size}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={6}>
                  <Card>
                    <Card.Header>
                      <div className="d-flex justify-content-between align-items-center">
                        <h6 className="mb-0">📋 {response.area2.area} Data</h6>
                        <DataSourceBadge source={response.area2.data_source} />
                      </div>
                    </Card.Header>
                    <Card.Body>
                      <div className="table-responsive">
                        <table className="table table-sm table-striped">
                          <thead>
                            <tr>
                              <th>Year</th>
                              <th>Price</th>
                              <th>Demand</th>
                              <th>Size</th>
                            </tr>
                          </thead>
                          <tbody>
                            {response.area2.table_data.map((row, index) => (
                              <tr key={index}>
                                <td>{row.year}</td>
                                <td>₹{row.price.toLocaleString()}</td>
                                <td>{row.demand}%</td>
                                <td>{row.size}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>

              {/* Export Section */}
              <Card className="mt-3">
                <Card.Body className="text-center">
                  <h6>💾 Export Comparison</h6>
                  <div className="d-flex justify-content-center gap-2">
                    <Button 
                      variant="success" 
                      onClick={() => handleDownload('excel')}
                      size="sm"
                    >
                      📊 Export to Excel
                    </Button>
                    <Button 
                      variant="outline-success" 
                      onClick={() => handleDownload('csv')}
                      size="sm"
                    >
                      📄 Export to CSV
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            </div>
          )}
        </Col>
      </Row>
    </Container>
  );
}

export default App;