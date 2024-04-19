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
import { Block } from './block';
import { History } from './history_block';
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


  const test = () => {
    axios.get("/api/recommend").then((response)=>{
      console.log(response.data)
      messageApi.success(JSON.stringify(response.data))
    })
  }
  const sendMessage = (newMessage?: string) => {
    let timestamp=new Date().getTime()
    const c: ChatMessage = {
      content: newMessage || inputText,
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
    });
  };

  const renderMessage = (msg:any) => {
    return (<><div id={msg?.id}>
      <Markdown>{String(msg?.content)}</Markdown>
      <Row gutter={16}>
      { (msg?.blocks??[]).map((e:any)=>{
        return( <Col span={5} key={e.title}>
          <Block 
          id = {e.id}
          title={e.title} 
          comment={e.bear_comment}
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
          let chatresponse = response.data.msg
          axios.get("/api/get_speech_token").then((response) => {  
            if (response.status === 200) {
              let access_token = response.data;
              let speechConfig = SpeechSDK.SpeechConfig.fromAuthorizationToken(access_token, "southeastasia");
              speechConfig.speechSynthesisVoiceName = voice;

              let synthesizer = new SpeechSDK.SpeechSynthesizer(speechConfig);
              synthesizer.speakTextAsync(chatresponse.content, function (result) {
                console.log("log:");
                console.log(result);
                synthesizer.close();
                synthesizer = undefined;
              }, function (err) {
                console.log("error:");
                console.log(err);
                synthesizer.close();
                synthesizer = undefined;
              });
            }
          });
           
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
  //load azure speech javascript
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://aka.ms/csspeech/jsbrowserpackageraw';
    script.async = true;
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  const startSpeechText = ()=>{
    axios.get("/api/get_speech_token").then((response) => {  
      if (response.status === 200) {
        let access_token = response.data;
        let speechConfig = SpeechSDK.SpeechConfig.fromAuthorizationToken(access_token, "southeastasia");
        speechConfig.speechRecognitionLanguage = "en-US";
        var audioConfig  = SpeechSDK.AudioConfig.fromDefaultMicrophoneInput();
        let recognizer = new SpeechSDK.SpeechRecognizer(speechConfig, audioConfig);
        setSpeechRecognizer(recognizer);

        recognizer.startContinuousRecognitionAsync (
          function () {
            console.log("mic started");
          },
          function (err) {
            console.log("mic error:");
            console.log(err);
            recognizer.close();
            setMicIcon(MicOff);
          }
        );

        recognizer.recognized = (s, e) => {
          console.log("speech recognised");
          // speech recognition output
          if (e.result.text.length > 0 && e.result.text!="undefined" && e.result.text!=""){
            const newText = e.result.text;
            console.log(newText);
            setInputText(newText);
            // console.log(inputText);
            sendMessage(newText);
          }
        }
      }


    });
  }

  const endSpeechText = ()=>{
    console.log("end speech to text");
    speechRecognizer.close();
  }

  const [voice, setVoice] = useState('en-US-BrianMultilingualNeural');

  let main_tab = <></>
  if(tab=="chat"){
    main_tab =<Col span={23}>
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
                  {/* <ActionIcon icon={LibraryBig} onClick={() => { test() }}/> */}
                  <ActionIcon icon={micIconRef} onClick={
                    () => {
                      if (micIconRef === MicIcon) {
                        setMicIcon(MicOff);
                        endSpeechText();
                      } else {
                        setMicIcon(MicIcon);
                        startSpeechText();
                      }
                    }                           
                   } />
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
  </Col>
  }

  if (tab=='market'){
    main_tab = <Col span={23}>    
    <History></History>
  </Col>
  }


  return (
    <ThemeProvider>
      {contextHolder}
      <Modal
        footer={<Button type={'primary'}>Demo</Button>}
        onCancel={handleCancel}
        onOk={handleOk}
        open={isModalOpen}
        title="Bear Config"
      >
        <Card title="Voice">
        <Radio.Group name="Voice" defaultValue={voice} onChange={(e)=>{setVoice(e.target.value);}}>
          <Radio value={'en-US-BrianMultilingualNeural'}>Polar Prince</Radio>
          <Radio value={'en-SG-LunaNeural'}>Sun Bear Soprano</Radio>
          <Radio value={'en-SG-WayneNeural'}>Grizzly Groove</Radio>
          <Radio value={'zh-CN-XiaochenNeural'}>Panda Pitch</Radio>
        </Radio.Group>
        </Card>
      </Modal>
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
      {main_tab}

      </Row>

    </ThemeProvider>
  );
};