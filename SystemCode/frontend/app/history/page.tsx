'use client';
import {
  ActionIcon,
  ChatInputActionBar,
  ChatInputArea,
  ChatSendButton,
  TokenTag,
  ChatList,
  ChatMessage,
  MessageModal,
  ChatItem,
  ActionsBar,
  Markdown,
  Header,
  
} from '@lobehub/ui';
import { Logo, SideNav } from '@lobehub/ui';
import { Eraser, Languages, MicIcon, MicOff, LucideIcon } from 'lucide-react';
import { Flexbox } from 'react-layout-kit';
import { ThemeProvider } from '@lobehub/ui';
import { useState, useRef, useEffect} from 'react';
import axios from "axios";
import { Row, Col, Card,Image, message, Button } from 'antd';
import { ImageGallery } from '@lobehub/ui';
import { Album, MessageSquare, Settings2 } from 'lucide-react';
import useSWR from 'swr'
import { Modal } from '@lobehub/ui';
import { access } from 'fs';
import { Content } from 'next/font/google';
// import * as SpeechSDK from 'microsoft-cognitiveservices-speech-sdk';
import { Radio } from 'antd';


export default function App(){
  const [messageApi, contextHolder] = message.useMessage();
  const scrollableRef = useRef<null | HTMLDivElement>(null);
  const [tab, setTab] = useState('chat')
  const [sessionKey, setSessionKey] = useState('')
  useEffect(() => {
    axios.get("/api/init_chat").then((response)=>{
        setSessionKey(response.data.session_key)
      }
    )
  }, []);
  console.log(sessionKey)

  const [isModalOpen, setIsModalOpen] = useState(false);
  const showModal = () => {
    setIsModalOpen(true);
  };
  const handleOk = () => {
    setIsModalOpen(false);
  };
  const handleCancel = () => {
    setIsModalOpen(false);
  };


  const [conversation, setConversation] = useState<ChatMessage[]>([]);
  const [micIconRef, setMicIcon] = useState<LucideIcon>(MicOff);
  const [speechRecognizer, setSpeechRecognizer] = useState<any>(null);

  useEffect(() => {
    // Check if the ref is attached to an element
    scrollableRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation]);

  const [inputText, setInputText] = useState<string>('');




  return (
    <ThemeProvider>
      {contextHolder}
      <Row><Col span={1}><SideNav
        style={{"width": "100%"}}       
        avatar={<img src="images/cinepaw_logo.webp"  />}
      topActions={
        <>
      <ActionIcon
        active={tab === 'chat'}
        icon={MessageSquare}
        onClick={() => setTab('chat')}
        size="large"
      />
      <ActionIcon
        active={tab === 'market'}
        icon={Album}
        onClick={() => setTab('market')}
        size="large"
      />
      </>
    }
      bottomActions={<ActionIcon icon={Settings2} onClick={showModal}/>}
      ></SideNav></Col>
      </Row>
    </ThemeProvider>
  );
};