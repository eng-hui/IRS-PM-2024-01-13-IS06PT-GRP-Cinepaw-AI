import { Card } from "antd";

interface BlockProps {
    title?: string;
    content?: any;
    image_url?: string;
    desc?:string;
}
const { Meta } = Card;

export const Block: React.FC<BlockProps> = (prop) => {
    return (
        <>
            <Card
                hoverable    
                cover={
                    <img
                        alt={prop.title}
                        src={prop.image_url}
                    />
                    }
            >
                <Meta title={prop.title} />
            </Card>
        </>
    )
}


