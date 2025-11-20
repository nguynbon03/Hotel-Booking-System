import React, { useState, useRef, useEffect } from 'react';
import { 
  ChatBubbleLeftRightIcon, 
  XMarkIcon, 
  PaperAirplaneIcon,
  SparklesIcon,
  UserIcon,
  ComputerDesktopIcon
} from '@heroicons/react/24/outline';
import { apiClient } from '@/lib/api';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  recommendations?: RoomRecommendation[];
}

interface RoomRecommendation {
  id: string;
  name: string;
  price: number;
  description: string;
  image_url: string;
  match_score: number;
  reasons: string[];
}

const AIChatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'bot',
      content: 'Hello! I\'m your AI room assistant. I can help you find the perfect room based on your preferences. What are you looking for?',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Call AI recommendation API
      const response = await apiClient.getRoomRecommendations({
        amenities: inputMessage,
        limit: 3
      });

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: generateBotResponse(inputMessage, response),
        timestamp: new Date(),
        recommendations: response.recommendations || []
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('AI recommendation error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: 'I apologize, but I\'m having trouble processing your request right now. Please try again or browse our rooms directly.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateBotResponse = (userInput: string, recommendations: any): string => {
    const input = userInput.toLowerCase();
    
    if (input.includes('luxury') || input.includes('premium') || input.includes('deluxe')) {
      return '✨ Perfect! I\'ve curated our finest luxury accommodations just for you. These rooms feature premium amenities and exceptional service:';
    } else if (input.includes('family') || input.includes('kids') || input.includes('children')) {
      return '👨‍👩‍👧‍👦 Wonderful! I\'ve selected family-friendly rooms with extra space, connecting rooms, and child-friendly amenities:';
    } else if (input.includes('business') || input.includes('work') || input.includes('meeting')) {
      return '💼 Excellent choice! Here are our business-optimized rooms with work desks, high-speed WiFi, and meeting facilities:';
    } else if (input.includes('budget') || input.includes('cheap') || input.includes('affordable') || input.includes('economy')) {
      return '💰 Smart choice! I\'ve found our best value rooms that don\'t compromise on comfort and quality:';
    } else if (input.includes('romantic') || input.includes('honeymoon') || input.includes('couple')) {
      return '💕 How romantic! I\'ve selected intimate rooms perfect for couples, with beautiful views and special amenities:';
    } else if (input.includes('view') || input.includes('ocean') || input.includes('city')) {
      return '🌅 Great taste! Here are rooms with spectacular views that will make your stay unforgettable:';
    } else if (input.includes('pool') || input.includes('spa') || input.includes('gym')) {
      return '🏊‍♂️ Perfect! I\'ve found rooms with easy access to our wellness facilities and recreational amenities:';
    } else if (input.includes('quiet') || input.includes('peaceful') || input.includes('relax')) {
      return '🧘‍♀️ Ideal for relaxation! These quiet rooms are located away from high-traffic areas for maximum tranquility:';
    } else {
      return '🎯 Based on your preferences, I\'ve personally selected these exceptional rooms that I think you\'ll love:';
    }
  };

  const handleQuickQuestion = (question: string) => {
    setInputMessage(question);
  };

  const handleRoomSelect = (roomId: string) => {
    window.open(`/room/${roomId}`, '_blank');
  };

  const quickQuestions = [
    "Show me luxury suites with premium amenities",
    "Family rooms perfect for kids and children",
    "Budget-friendly options with great value",
    "Rooms with stunning city or ocean views",
    "Business rooms with work facilities",
    "Romantic suites for couples and honeymoon",
    "Quiet rooms for peaceful relaxation",
    "Rooms near pool, spa and gym facilities"
  ];

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setIsOpen(true)}
          className="bg-primary-600 text-white p-4 rounded-full shadow-lg hover:bg-primary-700 transition-all duration-300 hover:scale-110"
        >
          <ChatBubbleLeftRightIcon className="w-6 h-6" />
        </button>
        <div className="absolute -top-12 right-0 bg-gray-900 text-white px-3 py-1 rounded-lg text-sm whitespace-nowrap">
          Ask AI for room recommendations
        </div>
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 w-96 h-[500px] bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col">
      {/* Header */}
      <div className="bg-primary-600 text-white p-4 rounded-t-lg flex items-center justify-between">
        <div className="flex items-center">
          <SparklesIcon className="w-5 h-5 mr-2" />
          <h3 className="font-semibold">AI Room Assistant</h3>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="text-white hover:text-gray-200 transition-colors"
        >
          <XMarkIcon className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex items-start space-x-2 max-w-[80%] ${
              message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
            }`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                message.type === 'user' 
                  ? 'bg-primary-600 text-white' 
                  : 'bg-gray-200 text-gray-600'
              }`}>
                {message.type === 'user' ? (
                  <UserIcon className="w-4 h-4" />
                ) : (
                  <ComputerDesktopIcon className="w-4 h-4" />
                )}
              </div>
              <div className={`rounded-lg p-3 ${
                message.type === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                <p className="text-sm">{message.content}</p>
                
                {/* Room Recommendations */}
                {message.recommendations && message.recommendations.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {message.recommendations.map((room) => (
                      <div
                        key={room.id}
                        onClick={() => handleRoomSelect(room.id)}
                        className="bg-white border border-gray-200 rounded-lg p-3 cursor-pointer hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-center space-x-3">
                          <img
                            src={room.image_url}
                            alt={room.name}
                            className="w-12 h-12 rounded-lg object-cover"
                          />
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900 text-sm">{room.name}</h4>
                            <p className="text-xs text-gray-600">${room.price}/night</p>
                            <div className="flex items-center mt-1">
                              <SparklesIcon className="w-3 h-3 text-yellow-500 mr-1" />
                              <span className="text-xs text-gray-500">{room.match_score}% match</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                <ComputerDesktopIcon className="w-4 h-4 text-gray-600" />
              </div>
              <div className="bg-gray-100 rounded-lg p-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Questions */}
      {messages.length <= 1 && (
        <div className="px-4 pb-2">
          <p className="text-xs text-gray-500 mb-2">Quick questions:</p>
          <div className="flex flex-wrap gap-1">
            {quickQuestions.slice(0, 3).map((question, index) => (
              <button
                key={index}
                onClick={() => handleQuickQuestion(question)}
                className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-2 py-1 rounded-full transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Ask me about rooms..."
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="bg-primary-600 text-white p-2 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PaperAirplaneIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIChatbot;
