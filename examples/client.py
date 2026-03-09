from ai_hub_agents import client
import argparse

def get_args() -> argparse.Namespace:
    """获取命令行参数"""
    parser = argparse.ArgumentParser(description='AI Hub Agents Client')
    parser.add_argument('--url', type=str, default='http://localhost:8000', help='URL')
    parser.add_argument('--query', type=str, default='你怎么看待人工智能？', help='查询')
    parser.add_argument('--user-name', type=str, default='user', help='用户名称')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()
    response = client.post(
        thread_id="example-client",
        url=args.url,
        query=args.query,
        user_name=args.user_name,
    )
    print(response)