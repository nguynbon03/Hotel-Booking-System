import React, { useState, useRef, useEffect } from 'react';
import { 
  ChatBubbleLeftRightIcon, 
  XMarkIcon, 
  PaperAirplaneIcon,
  UserIcon,
  UserCircleIcon,
  PhoneIcon,
  VideoCameraIcon,
  PhotoIcon,
  FaceSmileIcon
} from '@heroicons/react/24/outline';
import { CheckIcon } from '@heroicons/react/24/solid';

interface Message {
  id: string;
  type: 'user' | 'staff' | 'system';
  content: string;
  timestamp: Date;
  status: 'sending' | 'sent' | 'delivered' | 'read';
  staffName?: string;
  staffRole?: string;
  attachments?: string[];
}

interface StaffMember {
  id: string;
  name: string;
  role: string;
  avatar: string;
  status: 'online' | 'busy' | 'offline';
  department: string;
}

const LiveStaffChat: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: 'Welcome to Grand Palace Hotel Live Support! You\'re connected to our customer service team.',
      timestamp: new Date(),
      status: 'read'
    },
    {
      id: '2',
      type: 'staff',
      content: 'Hello! I\'m Sarah from the front desk. How can I assist you today? 😊',
      timestamp: new Date(),
      status: 'read',
      staffName: 'Sarah Johnson',
      staffRole: 'Front Desk Manager'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [staffTyping, setStaffTyping] = useState<string | null>(null);
  const [onlineStaff, setOnlineStaff] = useState<StaffMember[]>([
    {
      id: '1',
      name: 'Sarah Johnson',
      role: 'Front Desk Manager',
      avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150',
      status: 'online',
      department: 'Reception'
    },
    {
      id: '2',
      name: 'Michael Chen',
      role: 'Concierge',
      avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150',
      status: 'online',
      department: 'Guest Services'
    },
    {
      id: '3',
      name: 'Emma Rodriguez',
      role: 'Guest Relations',
      avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150',
      status: 'busy',
      department: 'Guest Relations'
    }
  ]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Simulate staff responses
  useEffect(() => {
    if (messages.length > 2 && messages[messages.length - 1].type === 'user') {
      const timer = setTimeout(() => {
        setStaffTyping('Sarah Johnson');
        setTimeout(() => {
          setStaffTyping(null);
          const responses = [
            "I'd be happy to help you with that! Let me check our system for you.",
            "That's a great question! I can assist you with booking modifications and special requests.",
            "Absolutely! I can help you with room upgrades, dining reservations, and local recommendations.",
            "Thank you for reaching out! I'm here to ensure your stay is perfect. What specific assistance do you need?",
            "I understand your concern. Let me connect you with the right department to resolve this quickly."
          ];
          
          const randomResponse = responses[Math.floor(Math.random() * responses.length)];
          
          const staffMessage: Message = {
            id: Date.now().toString(),
            type: 'staff',
            content: randomResponse,
            timestamp: new Date(),
            status: 'read',
            staffName: 'Sarah Johnson',
            staffRole: 'Front Desk Manager'
          };
          
          setMessages(prev => [...prev, staffMessage]);
        }, 2000);
      }, 1000);
      
      return () => clearTimeout(timer);
    }
  }, [messages]);

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
      status: 'sending'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    // Simulate message status updates
    setTimeout(() => {
      setMessages(prev => prev.map(msg => 
        msg.id === userMessage.id ? { ...msg, status: 'sent' } : msg
      ));
    }, 500);

    setTimeout(() => {
      setMessages(prev => prev.map(msg => 
        msg.id === userMessage.id ? { ...msg, status: 'delivered' } : msg
      ));
    }, 1000);

    setTimeout(() => {
      setMessages(prev => prev.map(msg => 
        msg.id === userMessage.id ? { ...msg, status: 'read' } : msg
      ));
    }, 1500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickActions = [
    "I need help with my booking",
    "Room service request",
    "Check-in/Check-out assistance",
    "Local recommendations",
    "Technical support",
    "Billing inquiry"
  ];

  const getMessageStatusIcon = (status: Message['status']) => {
    switch (status) {
      case 'sending':
        return <div className="w-3 h-3 border border-gray-400 border-t-transparent rounded-full animate-spin" />;
      case 'sent':
        return <CheckIcon className="w-3 h-3 text-gray-400" />;
      case 'delivered':
        return (
          <div className="flex">
            <CheckIcon className="w-3 h-3 text-gray-400" />
            <CheckIcon className="w-3 h-3 text-gray-400 -ml-1" />
          </div>
        );
      case 'read':
        return (
          <div className="flex">
            <CheckIcon className="w-3 h-3 text-blue-500" />
            <CheckIcon className="w-3 h-3 text-blue-500 -ml-1" />
          </div>
        );
      default:
        return null;
    }
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 left-6 z-50">
        <button
          onClick={() => setIsOpen(true)}
          className="bg-green-600 text-white p-4 rounded-full shadow-lg hover:bg-green-700 transition-all duration-300 hover:scale-110 relative"
        >
          <ChatBubbleLeftRightIcon className="w-6 h-6" />
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
        </button>
        <div className="absolute -top-12 left-0 bg-gray-900 text-white px-3 py-1 rounded-lg text-sm whitespace-nowrap">
          Chat with our staff
        </div>
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 left-6 z-50 w-96 h-[600px] bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col">
      {/* Header */}
      <div className="bg-green-600 text-white p-4 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="relative">
              <img
                src={onlineStaff[0]?.avatar}
                alt={onlineStaff[0]?.name}
                className="w-10 h-10 rounded-full border-2 border-white"
              />
              <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white"></div>
            </div>
            <div className="ml-3">
              <h3 className="font-semibold">Live Support</h3>
              <p className="text-xs text-green-100">
                {onlineStaff.filter(s => s.status === 'online').length} staff online
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button className="text-white hover:text-green-200 transition-colors">
              <PhoneIcon className="w-5 h-5" />
            </button>
            <button className="text-white hover:text-green-200 transition-colors">
              <VideoCameraIcon className="w-5 h-5" />
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:text-green-200 transition-colors"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Online Staff */}
      <div className="bg-gray-50 px-4 py-2 border-b">
        <div className="flex items-center space-x-2 overflow-x-auto">
          {onlineStaff.map((staff) => (
            <div key={staff.id} className="flex items-center space-x-1 bg-white px-2 py-1 rounded-full text-xs whitespace-nowrap">
              <div className="relative">
                <img
                  src={staff.avatar}
                  alt={staff.name}
                  className="w-6 h-6 rounded-full"
                />
                <div className={`absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border border-white ${
                  staff.status === 'online' ? 'bg-green-400' : 
                  staff.status === 'busy' ? 'bg-yellow-400' : 'bg-gray-400'
                }`}></div>
              </div>
              <span className="text-gray-700">{staff.name.split(' ')[0]}</span>
            </div>
          ))}
        </div>
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
              {message.type !== 'user' && (
                <div className="w-8 h-8 rounded-full flex items-center justify-center bg-gray-200">
                  {message.type === 'staff' ? (
                    <img
                      src={onlineStaff[0]?.avatar}
                      alt="Staff"
                      className="w-8 h-8 rounded-full"
                    />
                  ) : (
                    <UserCircleIcon className="w-5 h-5 text-gray-600" />
                  )}
                </div>
              )}
              
              <div className={`rounded-lg p-3 ${
                message.type === 'user'
                  ? 'bg-green-600 text-white'
                  : message.type === 'staff'
                  ? 'bg-gray-100 text-gray-800'
                  : 'bg-blue-50 text-blue-800 text-center'
              }`}>
                {message.type === 'staff' && message.staffName && (
                  <div className="text-xs text-gray-500 mb-1">
                    {message.staffName} • {message.staffRole}
                  </div>
                )}
                
                <p className="text-sm">{message.content}</p>
                
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs opacity-70">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                  {message.type === 'user' && (
                    <div className="ml-2">
                      {getMessageStatusIcon(message.status)}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {staffTyping && (
          <div className="flex justify-start">
            <div className="flex items-center space-x-2">
              <img
                src={onlineStaff[0]?.avatar}
                alt="Staff"
                className="w-8 h-8 rounded-full"
              />
              <div className="bg-gray-100 rounded-lg p-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">{staffTyping} is typing...</p>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      {messages.length <= 2 && (
        <div className="px-4 pb-2">
          <p className="text-xs text-gray-500 mb-2">Quick actions:</p>
          <div className="flex flex-wrap gap-1">
            {quickActions.slice(0, 3).map((action, index) => (
              <button
                key={index}
                onClick={() => setInputMessage(action)}
                className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-2 py-1 rounded-full transition-colors"
              >
                {action}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center space-x-2">
          <button className="text-gray-400 hover:text-gray-600 transition-colors">
            <PhotoIcon className="w-5 h-5" />
          </button>
          <button className="text-gray-400 hover:text-gray-600 transition-colors">
            <FaceSmileIcon className="w-5 h-5" />
          </button>
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim()}
            className="bg-green-600 text-white p-2 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PaperAirplaneIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default LiveStaffChat;
