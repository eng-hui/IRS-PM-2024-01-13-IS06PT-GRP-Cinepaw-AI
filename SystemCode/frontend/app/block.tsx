import { Card } from "antd";

interface BlockProps {
    id: number;
    title?: string;
    content?: any;
    image_url?: string;
    comment?: string;
    desc?:string;
}
const { Meta } = Card;

export const Block: React.FC<BlockProps> = (prop) => {
    return (
        <>
            <Card
                hoverable  
                onClick={()=>{window.open('https://www.themoviedb.org/movie/'+String(prop.id), '_blank');}}  
                cover={
                    <img
                        alt={prop.title}
                        src={prop.image_url}
                    />
                    }
            >
                <Meta title={prop.title} />
                🐻‍❄️: {prop.comment}
            </Card>
        </>
    )
}


