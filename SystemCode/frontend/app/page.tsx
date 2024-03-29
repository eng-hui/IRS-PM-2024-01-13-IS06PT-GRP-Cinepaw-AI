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
import { Row, Col, Card,Image } from 'antd';
import { ImageGallery } from '@lobehub/ui';
import { Block } from './block';
import { Album, MessageSquare, Settings2 } from 'lucide-react';
import { access } from 'fs';
import { Content } from 'next/font/google';




export default function App(){
  const scrollableRef = useRef<null | HTMLDivElement>(null);

  const [conversation, setConversation] = useState<ChatMessage[]>([]);
  const [micIconRef, setMocIcon] = useState<LucideIcon>(MicOff);
  const [speechRecognizer, setSpeechRecognizer] = useState<any>(null);

  useEffect(() => {
    // Check if the ref is attached to an element
    scrollableRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation]);

  const [inputText, setInputText] = useState<string>('');

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

    axios.post("/api/chat_test", { "text": newMessage || inputText, "history": conversation }).then((response) => {
      console.log(response.data);
      const chatResponse = response.data;
      setConversation(oldArray => [...oldArray, response.data]);
      return chatResponse;
    }).then(chatResponse => { 
      // Text to speech
      axios.get("/api/get_speech_token").then((response) => {  
        if (response.status === 200) {
          let access_token = response.data;
          let speechConfig = SpeechSDK.SpeechConfig.fromAuthorizationToken(access_token, "southeastasia");
          speechConfig.speechSynthesisVoiceName = "en-US-BrianMultilingualNeural";
          
          let synthesizer = new SpeechSDK.SpeechSynthesizer(speechConfig);
          synthesizer.speakTextAsync(chatResponse.content, function (result) {
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
            setMocIcon(MicOff);
          }
        );

        recognizer.recognized = (s, e) => {
          console.log("speech recognised");
          // speech recognition output
          if (e.result.text.length > 0 && e.result.text!="undefined" && e.result.text!=""){
            const newText = e.result.text;
            console.log(newText);
            setInputText(newText);
            console.log(inputText);
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

  return (
    <ThemeProvider>
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
                      <ActionIcon icon={micIconRef} onClick={
                        () => {
                          if (micIconRef === MicIcon) {
                            setMocIcon(MicOff);
                            endSpeechText();
                          } else {
                            setMocIcon(MicIcon);
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
      </Row>

    </ThemeProvider>
  );
};