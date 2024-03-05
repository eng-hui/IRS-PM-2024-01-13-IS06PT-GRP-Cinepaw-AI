'use client'
import {
  ActionIcon,
  ChatInputActionBar,
  ChatInputArea,
  ChatSendButton,
  TokenTag,
  ChatList,
  ChatMessage,
  MessageModal,
  ChatItem
} from '@lobehub/ui';
import { Eraser, Languages } from 'lucide-react';
import { Flexbox } from 'react-layout-kit';
import { ThemeProvider } from '@lobehub/ui';
import { useState } from 'react';
import axios from "axios"


export default () => {

  const [conversation, setConversation] = useState<ChatMessage[]>([])
  const [inputText, setInputText] = useState<string>('')
  const sendMessage = () => {
    const c:ChatMessage = {
      content: inputText,
      createAt: 1_686_437_950_084,
      extra: {},
      id: '1',
      meta: {
        avatar: 'https://images.unsplash.com/photo-1568162603664-fcd658421851?q=80&w=2881&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        title: 'CanisMinor',
      },
      role: 'user',
      updateAt: 1_686_437_950_084,
    }
    setConversation(oldArray => [...oldArray, c])
    axios.post("/api/chat_test", {"text":inputText, "history":conversation.slice(0, -1)}).then((response)=>{
      console.log(response.data)
      setConversation(oldArray => [...oldArray, response.data])
    })
  }
  return (
    <ThemeProvider>
    <div>
      
  <Flexbox style={{ height: 300, position: 'relative' }}>
  <ChatList data={conversation}
          renderMessages={{
            default: ({ id, content }) => <div id={id}>{content}</div>,
          }}
  >

  </ChatList>

  </Flexbox>
  <Flexbox style={{ height: 200, position: 'relative' }}>
    <ChatInputArea onSend={()=>sendMessage()} onInput={(value)=>{setInputText(value)}}
    bottomAddons={<ChatSendButton/>}
    topAddons={
      <ChatInputActionBar
        leftAddons={
          <>
            <ActionIcon icon={Languages} />
            <ActionIcon icon={Eraser} />
            <TokenTag maxValue={5000} value={1000} />
          </>
        }
      />
    }
  />
  </Flexbox>
  
  </div>
  </ThemeProvider>
  );
};