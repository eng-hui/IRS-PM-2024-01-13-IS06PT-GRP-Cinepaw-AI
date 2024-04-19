'use client';
import { Card } from "antd";
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
import { Row, Col,Image, message, Button } from 'antd';
import { ImageGallery } from '@lobehub/ui';
import { Album, MessageSquare, Settings2 } from 'lucide-react';
import useSWR from 'swr'
import { Modal } from '@lobehub/ui';
import { access } from 'fs';
import { Content } from 'next/font/google';

const { Meta } = Card;

export const History: React.FC = (prop) => {
    const [data, setData] = useState([])
    useEffect(() => {
        axios.get("/api/load_user_history").then((response)=>{
            console.log(response.data)
            setData(response.data)
          }
        )
      }, []);    
    return (
        <Row gutter={16} style={{marginTop:'20px', marginLeft:'20px'}}>
            {(data??[]).map((e:any)=>{
                return (
                <Col span={5}>
                <Card
                    hoverable  
                    onClick={()=>{window.open('https://www.themoviedb.org/movie/'+String(e.id), '_blank');}}  
                    cover={
                        <img
                            alt={e.title}
                            src={"https://media.themoviedb.org/t/p/w440_and_h660_face"+e.poster_path}
                        />
                        }
                >
                    <Meta title={e.title} />
                    😊: {e.quote}
                </Card>
                </Col>)
            })}
        </Row>
    )
}


