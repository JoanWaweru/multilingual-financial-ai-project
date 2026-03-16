'use client'

import { useState } from 'react'
import { User, Bot, ThumbsUp, ThumbsDown, Pencil } from 'lucide-react'
import { Message } from '@/types'
import { submitFeedback } from '@/lib/api'

interface MessageBubbleProps {
  message: Message & {
    evidence?: Array<{ text: string; source: string; similarity: number }>
  }
  sessionId: string
  canEdit?: boolean
  onEdit?: (content: string) => void
}

function formatAssistantMessage(text: string): { __html: string } {
  const escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

  const noHeadings = escaped
    .split('\n')
    .map((line) => line.replace(/^#{1,6}\s*/g, ''))
    .join('\n')

  const withBold = noHeadings.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  const withLineBreaks = withBold.replace(/\n/g, '<br />')

  return { __html: withLineBreaks }
}

export default function MessageBubble({ message, sessionId, canEdit, onEdit }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const formattedContent = !isUser ? formatAssistantMessage(message.content) : null
  const [feedbackSent, setFeedbackSent] = useState(false)

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex items-start space-x-2 max-w-[80%] ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-primary-600' : 'bg-gray-600'
        }`}>
          {isUser ? (
            <User className="w-5 h-5 text-white" />
          ) : (
            <Bot className="w-5 h-5 text-white" />
          )}
        </div>
        <div className={`rounded-lg px-4 py-3 ${
          isUser 
            ? 'bg-primary-600 text-white' 
            : 'bg-gray-100 text-gray-900'
        }`}>
          {isUser ? (
            <div className="space-y-1">
              <p className="whitespace-pre-wrap break-words">{message.content}</p>
              {canEdit && onEdit && (
                <button
                  type="button"
                  onClick={() => onEdit(message.content)}
                  className="mt-1 inline-flex items-center space-x-1 text-[10px] text-primary-100/90 hover:text-white"
                >
                  <Pencil className="w-3 h-3" />
                  <span>Edit and resend</span>
                </button>
              )}
            </div>
          ) : (
            <p
              className="whitespace-pre-wrap break-words"
              dangerouslySetInnerHTML={formattedContent ?? undefined}
            />
          )}
          
          {!isUser && message.confidence !== undefined && (
            <div className="mt-2 pt-2 border-t border-gray-300">
              <div className="flex items-center justify-between text-xs text-gray-600">
                <span>Confidence: {(message.confidence * 100).toFixed(0)}%</span>
              </div>
              {!feedbackSent && (
                <div className="mt-2 flex items-center space-x-2 text-xs text-gray-600">
                  <span>Helpful?</span>
                  <button
                    onClick={async () => {
                      await submitFeedback(sessionId, 5)
                      setFeedbackSent(true)
                    }}
                    className="flex items-center space-x-1 hover:text-gray-900"
                  >
                    <ThumbsUp className="w-3 h-3" />
                    <span>Yes</span>
                  </button>
                  <button
                    onClick={async () => {
                      await submitFeedback(sessionId, 2)
                      setFeedbackSent(true)
                    }}
                    className="flex items-center space-x-1 hover:text-gray-900"
                  >
                    <ThumbsDown className="w-3 h-3" />
                    <span>No</span>
                  </button>
                </div>
              )}
              {feedbackSent && (
                <div className="mt-2 text-xs text-gray-500">Thanks for your feedback.</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

