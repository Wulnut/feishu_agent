# feishu api limit

## feishu openapi limit

飞书开放平台各接口的QPS限制如下：

### 1. 飞书人事相关接口

- **查询岗位信息**：5 次/秒，详情参考[接口频率限制](https://go.feishu.cn/s/5_sDxlNNQ02)
- **创建成本分摊**：3 次/秒，详情参考[接口频率限制](https://go.feishu.cn/s/5_sDxlNNQ02)

### 2. 消息相关接口

- **发送仅特定人可见的消息卡片**：1000 次/分钟、50 次/秒，详情参考[接口频率限制](https://go.feishu.cn/s/5_sDxlNNQ02)
- **转发消息**：1000 次/分钟、50 次/秒，详情参考[接口频率限制](https://go.feishu.cn/s/5_sDxlNNQ02)
- **回复消息**：向同一用户发送消息限频为5 QPS，向同一群组发送消息限频为群内机器人共享5 QPS
- **合并转发消息**：向同一用户发送消息限频为5 QPS，向同一群组发送消息限频为群内机器人共享5 QPS
- **转发话题**：向同一用户发送消息限频为5 QPS，向同一群组发送消息限频为群内机器人共享5 QPS

### 3. 云文档相关接口

- **分片上传素材-完成上传**：5 QPS，10000 次/天
- **分片上传文件-完成上传**：5 QPS，10000 次/天
- **移动文件或文件夹**：20 次/分钟，详情参考[接口频率限制](https://go.feishu.cn/s/5_sDxlNNQ02)
- **创建文件快捷方式**：5 次/秒，详情参考[接口频率限制](https://go.feishu.cn/s/5_sDxlNNQ02)
- **上传素材**：5 QPS，10000 次/天
- **分片上传素材-上传分片**：5 QPS，10000 次/天

### 4. AI能力相关接口

- **识别文件中的名片**：10 次/秒，详情参考[接口频率限制](https://go.feishu.cn/s/5_sDxlNNQ02)
- **识别文件中的银行卡**：10 次/秒，详情参考[接口频率限制](https://go.feishu.cn/s/5_sDxlNNQ02)
- **识别图片中的文字**：特殊频控，详情参考[接口频率限制](https://go.feishu.cn/s/5_sDxlNNQ02)
- **识别文本语种**：特殊频控，详情参考[接口频率限制](https://go.feishu.cn/s/5_sDxlNNQ02)
- **识别文件中的身份证**：10 次/秒，详情参考[接口频率限制](https://go.feishu.cn/s/5_sDxlNNQ02)
- **识别文件中的台湾居民来往大陆通行证**：10 次/秒，详情参考[接口频率限制](https://go.feishu.cn/s/5_sDxlNNQ02)
- **提取文件中的合同字段**：10 次/秒，详情参考[接口频率限制](https://go.feishu.cn/s/5_sDxlNNQ02)

### 通用说明

- 部分接口标注为"特殊频控"，具体限制需参考各接口文档中的说明
- 同租户下的应用可能共享租户级别的QPS限制，如AI能力接口中的单租户限流
- 当接口调用频率超过限制时，会返回相应的错误码（如429状态码和1161604错误码），建议降低请求频率后重试

### 服务端 API 调用限制

服务端 API 对每个 Token 调用单个接口均限制了 15 QPS 的访问限制，请合理设计服务端 API 调用逻辑。部分非 15QPS 限制的接口明细如下

- 接口：[POST]/open_api/view/v1/update_condition_view
- 限制：同时限制 15 QPS 和 450 QPM

- 接口:[POST]/open_api/work_items/filter_across_project
- 限制: 同时限制 15 QPS 和 450 QPM  

- 接口:[POST]/open_api/work_item/subtask/search
- 限制: 同时限制 15 QPS 和 450 QPM  

- 接口:[POST]/open_api/:project_key/work_item/:work_item_type_key/search/params
- 限制: 同时限制 15 QPS 和 450 QPM  

- 接口:[POST]/open_api/:project_key/work_item/filter
- 限制: 同时限制 15 QPS 和 450 QPM  

- 接口:[POST]/open_api/:project_key/work_item/:work_item_type_key/:work_item_id/search_by_relation
- 限制:10 QPS

- 接口:[POST]/open_api/work_item/actual_time/update
- 限制:10 QPS
