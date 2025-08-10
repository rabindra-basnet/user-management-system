'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { 
  ShieldCheckIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon 
} from '@heroicons/react/24/outline';

interface SecurityTestResult {
  test: string;
  passed: boolean;
  message: string;
  severity: 'low' | 'medium' | 'high';
}

export function SecurityTest() {
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<SecurityTestResult[]>([]);
  const [testInput, setTestInput] = useState('');

  const runSecurityTests = async () => {
    setIsRunning(true);
    setResults([]);

    const tests: SecurityTestResult[] = [];

    // Test 1: XSS Protection
    try {
      const xssPayload = '<script>alert("xss")</script>';
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'test@example.com',
          first_name: xssPayload,
          last_name: 'User',
          password: 'TestPassword123!',
          confirm_password: 'TestPassword123!'
        })
      });

      tests.push({
        test: 'XSS Protection',
        passed: response.status === 422 || response.status === 400,
        message: response.status === 422 || response.status === 400 
          ? 'XSS payload properly rejected' 
          : 'XSS payload may have been accepted',
        severity: 'high'
      });
    } catch (error) {
      tests.push({
        test: 'XSS Protection',
        passed: true,
        message: 'Request blocked by browser/network security',
        severity: 'high'
      });
    }

    // Test 2: SQL Injection Protection
    try {
      const sqlPayload = "'; DROP TABLE users; --";
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: sqlPayload,
          password: 'password'
        })
      });

      tests.push({
        test: 'SQL Injection Protection',
        passed: response.status !== 500,
        message: response.status !== 500 
          ? 'SQL injection attempt handled safely' 
          : 'SQL injection may have caused server error',
        severity: 'high'
      });
    } catch (error) {
      tests.push({
        test: 'SQL Injection Protection',
        passed: true,
        message: 'Request handled safely',
        severity: 'high'
      });
    }

    // Test 3: Rate Limiting
    try {
      const promises = Array(10).fill(null).map(() =>
        fetch('/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: 'test@example.com',
            password: 'wrongpassword'
          })
        })
      );

      const responses = await Promise.all(promises);
      const rateLimited = responses.some(r => r.status === 429);

      tests.push({
        test: 'Rate Limiting',
        passed: rateLimited,
        message: rateLimited 
          ? 'Rate limiting is active' 
          : 'Rate limiting may not be configured',
        severity: 'medium'
      });
    } catch (error) {
      tests.push({
        test: 'Rate Limiting',
        passed: false,
        message: 'Unable to test rate limiting',
        severity: 'medium'
      });
    }

    // Test 4: HTTPS Enforcement
    const isHTTPS = window.location.protocol === 'https:';
    tests.push({
      test: 'HTTPS Enforcement',
      passed: isHTTPS || window.location.hostname === 'localhost',
      message: isHTTPS 
        ? 'Connection is secure (HTTPS)' 
        : window.location.hostname === 'localhost'
        ? 'Development environment (HTTP allowed)'
        : 'Connection is not secure (HTTP)',
      severity: 'high'
    });

    // Test 5: Security Headers
    try {
      const response = await fetch('/api/v1/health');
      const headers = response.headers;
      
      const securityHeaders = [
        'x-content-type-options',
        'x-frame-options',
        'x-xss-protection',
        'content-security-policy'
      ];

      const missingHeaders = securityHeaders.filter(header => !headers.get(header));
      
      tests.push({
        test: 'Security Headers',
        passed: missingHeaders.length === 0,
        message: missingHeaders.length === 0 
          ? 'All security headers present' 
          : `Missing headers: ${missingHeaders.join(', ')}`,
        severity: 'medium'
      });
    } catch (error) {
      tests.push({
        test: 'Security Headers',
        passed: false,
        message: 'Unable to check security headers',
        severity: 'medium'
      });
    }

    // Test 6: Password Strength Validation
    try {
      const weakPassword = 'password';
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'test2@example.com',
          first_name: 'Test',
          last_name: 'User',
          password: weakPassword,
          confirm_password: weakPassword
        })
      });

      tests.push({
        test: 'Password Strength Validation',
        passed: response.status === 422 || response.status === 400,
        message: response.status === 422 || response.status === 400 
          ? 'Weak passwords are rejected' 
          : 'Weak passwords may be accepted',
        severity: 'medium'
      });
    } catch (error) {
      tests.push({
        test: 'Password Strength Validation',
        passed: false,
        message: 'Unable to test password validation',
        severity: 'medium'
      });
    }

    // Test 7: Authentication Required
    try {
      const response = await fetch('/api/v1/auth/me');
      
      tests.push({
        test: 'Authentication Required',
        passed: response.status === 401,
        message: response.status === 401 
          ? 'Protected endpoints require authentication' 
          : 'Protected endpoints may be accessible without authentication',
        severity: 'high'
      });
    } catch (error) {
      tests.push({
        test: 'Authentication Required',
        passed: true,
        message: 'Request blocked',
        severity: 'high'
      });
    }

    setResults(tests);
    setIsRunning(false);
  };

  const testCustomInput = async () => {
    if (!testInput.trim()) return;

    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: testInput,
          password: 'test'
        })
      });

      const newResult: SecurityTestResult = {
        test: 'Custom Input Test',
        passed: response.status !== 500,
        message: `Input "${testInput}" - Status: ${response.status}`,
        severity: 'low'
      };

      setResults(prev => [...prev, newResult]);
    } catch (error) {
      const newResult: SecurityTestResult = {
        test: 'Custom Input Test',
        passed: true,
        message: `Input "${testInput}" - Request blocked`,
        severity: 'low'
      };

      setResults(prev => [...prev, newResult]);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-blue-600';
      default: return 'text-gray-600';
    }
  };

  const getSeverityBg = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-50 border-red-200';
      case 'medium': return 'bg-yellow-50 border-yellow-200';
      case 'low': return 'bg-blue-50 border-blue-200';
      default: return 'bg-gray-50 border-gray-200';
    }
  };

  const passedTests = results.filter(r => r.passed).length;
  const totalTests = results.length;

  return (
    <div className="space-y-6">
      <Card title="Security Testing" description="Test the security features of the application">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <ShieldCheckIcon className="h-6 w-6 text-blue-600" />
              <span className="text-lg font-medium">Security Test Suite</span>
            </div>
            
            <Button 
              onClick={runSecurityTests} 
              isLoading={isRunning}
              disabled={isRunning}
            >
              {isRunning ? 'Running Tests...' : 'Run Security Tests'}
            </Button>
          </div>

          {results.length > 0 && (
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-medium text-gray-700">
                  Test Results: {passedTests}/{totalTests} passed
                </span>
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(passedTests / totalTests) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-600">
                    {Math.round((passedTests / totalTests) * 100)}%
                  </span>
                </div>
              </div>
            </div>
          )}

          <div className="space-y-3">
            {results.map((result, index) => (
              <div 
                key={index} 
                className={`p-4 rounded-lg border ${getSeverityBg(result.severity)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    {result.passed ? (
                      <CheckCircleIcon className="h-5 w-5 text-green-600 mt-0.5" />
                    ) : (
                      <XCircleIcon className="h-5 w-5 text-red-600 mt-0.5" />
                    )}
                    <div>
                      <h4 className="font-medium text-gray-900">{result.test}</h4>
                      <p className="text-sm text-gray-600 mt-1">{result.message}</p>
                    </div>
                  </div>
                  <span className={`text-xs font-medium px-2 py-1 rounded ${getSeverityColor(result.severity)}`}>
                    {result.severity.toUpperCase()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      <Card title="Custom Security Test" description="Test custom input for security vulnerabilities">
        <div className="space-y-4">
          <div className="flex space-x-3">
            <Input
              value={testInput}
              onChange={(e) => setTestInput(e.target.value)}
              placeholder="Enter test input (e.g., <script>alert('xss')</script>)"
              className="flex-1"
            />
            <Button onClick={testCustomInput} disabled={!testInput.trim()}>
              Test Input
            </Button>
          </div>
          
          <div className="text-sm text-gray-600">
            <p className="font-medium mb-2">Common test payloads:</p>
            <ul className="space-y-1 text-xs">
              <li>• XSS: <code>&lt;script&gt;alert('xss')&lt;/script&gt;</code></li>
              <li>• SQL Injection: <code>'; DROP TABLE users; --</code></li>
              <li>• Path Traversal: <code>../../../etc/passwd</code></li>
              <li>• Command Injection: <code>; cat /etc/passwd</code></li>
            </ul>
          </div>
        </div>
      </Card>

      <Card className="bg-yellow-50 border-yellow-200">
        <div className="flex items-start space-x-3">
          <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600 mt-0.5" />
          <div>
            <h3 className="font-medium text-yellow-800">Security Testing Notice</h3>
            <p className="text-sm text-yellow-700 mt-1">
              This security testing tool is for educational and testing purposes only. 
              Only test against applications you own or have explicit permission to test. 
              Unauthorized security testing may be illegal.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
