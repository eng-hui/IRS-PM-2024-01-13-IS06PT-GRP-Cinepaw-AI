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
import { Logo, SideNav } from '@lobehub/ui';
import { Eraser, Languages, LibraryBig } from 'lucide-react';
import { Flexbox } from 'react-layout-kit';
import { ThemeProvider } from '@lobehub/ui';
import { useState, useRef, useEffect} from 'react';
import axios from "axios";
import { Row, Col, Card,Image, message } from 'antd';
import { ImageGallery } from '@lobehub/ui';
import { Block } from './block';
import { Album, MessageSquare, Settings2 } from 'lucide-react';
import useSWR from 'swr'
import test from 'node:test';





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


  const [conversation, setConversation] = useState<ChatMessage[]>([]);
  useEffect(() => {
    // Check if the ref is attached to an element
    scrollableRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation]);

  const [inputText, setInputText] = useState<string>('');

  const test = () => {
    axios.get("/api/recommend").then((response)=>{
      console.log(response.data)
      messageApi.success(JSON.stringify(response.data))
    })
  }
  const sendMessage = () => {
    var timestamp=new Date().getTime()
    const c: ChatMessage = {
      content: inputText,
      createAt: timestamp,
      extra: {},
      id: timestamp.toString(),
      meta: {
        avatar: 'https://images.unsplash.com/photo-1568162603664-fcd658421851?q=80&w=2881&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        title: 'CanisMinor',
      },
      role: 'user',
      updateAt: timestamp,
    };

    setConversation(oldArray => [...oldArray, c]);
    setInputText('');

    axios.post("/api/chat_input", { "text": inputText, "history": conversation, "session_key":sessionKey}).then((response) => {
      console.log(response.data);
      // setConversation(oldArray => [...oldArray, response.data]);
    });
  };

  const renderMessage = (msg:any) => {
    return (<><div id={msg?.id}>
      <Markdown>{String(msg?.content)}</Markdown>
      <Row>
      { (msg?.blocks??[]).map((e:any)=>{
        return( <Col span={3} key={e.title}>
          <Block title={e.title} 
          image_url={"https://media.themoviedb.org/t/p/w440_and_h660_face"+e.poster_path}
          ></Block></Col>
        )
      })}
      </Row>
      {msg?.image?<Image width={200} src={msg?.image}/>:<></>}
    </div>
      </>)
  }


  //fetch result
  const [getFlag, setGetFlag] = useState(true)
  const fetcher = (url:string) => {
    let data 
    let terror
    if(getFlag){
      axios.get(url).then((response) =>{
        data = response.data;
        if(data.success){
          setConversation(oldArray => [...oldArray, response.data.msg])
        }else{
          console.log(data)
        }
      }).catch((error) =>{
        terror = error
        console.log(error)
      })
    }
    return {"data":data, "error":terror}
  }
  const { data, error} = useSWR("/api/sub_message/"+String(sessionKey), fetcher, { refreshInterval: 1000 });

  return (
    <ThemeProvider>
      {contextHolder}
        <Row>
        <Col span={3}>
          <Image style={{marginTop: "10px", marginLeft: "10px"}} width={100} src="/Images/cinepaw_logo.webp" alt="logo" />
        </Col>
        <Col span={21}>
        </Col> 
      </Row>
      <Row><Col span={1}><SideNav
        style={{"width": "100%"}}       
        avatar={<Logo size={40} />}
      topActions={<ActionIcon
        active={tab === 'chat'}
        icon={MessageSquare}
        onClick={() => setTab('chat')}
        size="large"
      />}
      bottomActions={<ActionIcon icon={Settings2} />}
      ></SideNav></Col>
      <Col span={23}>
        <Row>
          <Col span={24} style={{ height: '400px', overflow: 'auto' }}>
            <ChatList
              data={conversation}
              renderMessages={{
                default: (msg) => {
                  return renderMessage(msg)
                },
              }}
            ></ChatList>
            <div ref={scrollableRef} style={{ overflowAnchor: 'auto' }}></div>
          </Col>
        </Row>
        <Row style={{ marginTop: '20px' }} >
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
                      <ActionIcon icon={LibraryBig} onClick={() => { test() }}/>
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
      </Col>
      </Row>

    </ThemeProvider>
  );
};