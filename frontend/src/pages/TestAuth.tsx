import React from 'react';
import { apiClient } from '@/lib/api';

const TestAuth: React.FC = () => {
  const [result, setResult] = React.useState<string>('');

  const testLogin = async () => {
    try {
      setResult('Testing login...');
      const response = await apiClient.login({
        email: 'nguyencxh2k4@gmail.com',
        password: 'admin@123'
      });
      setResult('✅ Login successful: ' + JSON.stringify(response));
    } catch (error: any) {
      setResult('❌ Login failed: ' + error.message);
    }
  };

  const testRegister = async () => {
    try {
      setResult('Testing register...');
      // Test register API call
      const response = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'test123',
          full_name: 'Test User',
          phone: '1234567890'
        })
      });
      const data = await response.json();
      setResult('✅ Register response: ' + JSON.stringify(data));
    } catch (error: any) {
      setResult('❌ Register failed: ' + error.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow">
        <h1 className="text-2xl font-bold mb-6">🧪 Auth API Test</h1>
        
        <div className="space-y-4 mb-6">
          <button
            onClick={testLogin}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Test Login API
          </button>
          
          <button
            onClick={testRegister}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 ml-4"
          >
            Test Register API
          </button>
        </div>
        
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">Result:</h3>
          <pre className="text-sm whitespace-pre-wrap">{result}</pre>
        </div>
        
        <div className="mt-6 text-sm text-gray-600">
          <p><strong>Backend API:</strong> http://localhost:8000</p>
          <p><strong>Available endpoints:</strong></p>
          <ul className="list-disc list-inside ml-4">
            <li>POST /auth/login</li>
            <li>POST /auth/register</li>
            <li>POST /auth/logout</li>
            <li>GET /users/me</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default TestAuth;
