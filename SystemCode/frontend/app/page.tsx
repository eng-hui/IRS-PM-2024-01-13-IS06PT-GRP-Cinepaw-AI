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
  
} from '@lobehub/ui';


import { Eraser, Languages } from 'lucide-react';
import { Flexbox } from 'react-layout-kit';
import { ThemeProvider } from '@lobehub/ui';
import { useState, useRef, useEffect } from 'react';
import axios from "axios";
import { Row, Col, Card, Image } from 'antd';
import { Scope_One } from 'next/font/google';


export default () => {
  const scrollableRef = useRef<null | HTMLDivElement>(null);

  const [conversation, setConversation] = useState<ChatMessage[]>([]);
  useEffect(() => {
    // Check if the ref is attached to an element
    scrollableRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation]);

  const [inputText, setInputText] = useState<string>('');

  const sendMessage = () => {
    const c: ChatMessage = {
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
    };

    setConversation(oldArray => [...oldArray, c]);
    setInputText('');

    axios.post("/api/chat_test", { "text": inputText, "history": conversation.slice(0, -1) }).then((response) => {
      console.log(response.data);
      setConversation(oldArray => [...oldArray, response.data]);
    });
  };

  return (
    <ThemeProvider>
        <Row className="header-style">
        <Col span={3}>
          <Image style={{marginTop: "10px", marginLeft: "10px"}} width={100} src="/Images/cinepaw_logo.webp" alt="logo" />
        </Col>
        <Col span={21}>
        </Col> 
      </Row>
      <Row>
        <Col span={24} style={{ height: '400px', overflow: 'auto' }}>
          <ChatList
            data={conversation}
            renderMessages={{
              default: (msg) => {
                console.log('yyyyyyyyyyyyyy');
                console.log(msg ?? '');
                return <div id={msg?.id}><Markdown children={String(msg?.content)}></Markdown></div>;
              },
            }}
          ></ChatList>
          <div ref={scrollableRef} style={{ overflowAnchor: 'auto' }}></div>
        </Col>
      </Row>
      <Row style={{ marginTop: '20px' }}>
        <Col span={24}>
          <Card style={{backgroundColor: "FFFFFF"}}>
          <ChatInputArea
            onSend={() => sendMessage()}
            value={inputText}
            onInput={(value) => { setInputText(value) }}
            bottomAddons={<ChatSendButton />}
            topAddons={
              <ChatInputActionBar
                leftAddons={
                  <>
                    <ActionIcon icon={Languages} />
                    <ActionIcon icon={Eraser} onClick={() => { setInputText('') }} />
                    {/* <TokenTag maxValue={5000} value</div>={1000} /> */}
                  </>
                }
              />
            }
          />
          </Card>
        </Col>
      </Row>
    </ThemeProvider>
  );
};