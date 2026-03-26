# coding: utf-8

import requests

if __name__ == '__main__':
    base_url = "http://127.0.0.1:8000"
    url = base_url + '/mcp'
    session_header = "mcp-session-id"
    # session
    session_resp = requests.post(url, json={
        "jsonrpc": "2.0",
        "method": "session.create",
        "params": {},
        "id": 1
    }, headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "mcp-session-id": None
    })
    session_id = session_resp.headers[session_header]
    print(f"Session ID: {session_id}")
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json, text/event-stream",
        session_header: session_id
    }
    # initialize
    init_resp = requests.post(url, json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "my-client",
                "version": "0.1.0"
            }
        }
    }, headers=headers)
    print("initialize:", init_resp.text)
    # initialize notification (no params needed)
    notify_resp = requests.post(url, json={
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }, headers=headers)
    print("initialize notifications:", notify_resp.text)
    print()

    # call tools/list
    try:
        resp = requests.post(url, json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/list",
            "params": {}
        }, headers=headers)
        print("tools/list:", resp.text)
    except Exception as e:
        print("tools/list error:", e)

    # call data generation
    # try:
    #     resp = requests.post(url, json={
    #         "jsonrpc": "2.0",
    #         "method": "tools/call",
    #         "params": {
    #             "name": "data_generation",
    #             "arguments": {
    #                 "generate_type": "hot_topic",
    #                 "params": {"top_n": "5"}
    #             }
    #         },
    #         "id": 4
    #     }, headers=headers)
    #     print("call data_generation", resp.content.decode('utf-8'))
    # except Exception as e:
    #     print(e)

    # call model evaluation
    # try:
    #     resp = requests.post(url, json={
    #         "jsonrpc": "2.0",
    #         "method": "tools/call",
    #         "params": {
    #             "name": "model_evaluation",
    #             "arguments": {
    #                 "evaluate_type": "knowledge-authentic_and_accurate-general",
    #                 "params": {
    #                     "{{query}}": "ZEEKR 009与奔驰 V 级的动力性能对比如何？",
    #                     "{{reply}}": "ZEEKR 009动力强劲，电动驱动响应迅速。奔驰 V 级动力平稳。ZEEKR 009在加速和动力输出的直接性上有优势，能带来更畅快的驾驶感受。",
    #                     "{{base_time}}": "2025-09-16",
    #                 }
    #             }
    #         },
    #         "id": 5
    #     }, headers=headers)
    #     print("call model_evaluation", resp.content.decode('utf-8'))
    # except Exception as e:
    #     print(e)
