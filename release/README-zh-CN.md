# MPDXN 翼聊 AI · TestFlight 发布说明

## 当前状态
- 2026-10-13 夏威夷时间，无签名 iOS 主 App 和键盘扩展通过 GitHub Actions 编译。
- 35 项 Swift 共享逻辑测试通过；这不代表已签名或已进入 TestFlight。
- 原项目来源：https://github.com/jev-chat/jev-chat-jarvis-ios （MIT，保留 LICENSE / NOTICE，独立衍生版不得冒充原作者）。
- 当前独立分支：ci/jev-ios-unsigned-20261013。原有 main 不改动。

## 苹果必须提供的发布权限
普通免费 Apple ID 无权通过 TestFlight 发布自己的构建。
发布必须有 Apple Developer Program 有效会员（美国每年 $99），或现有付费开发者团队授权。
可在 iPhone 安装 Apple Developer App → Account → Enroll Now 申请会员，无须买 Mac。
官方：https://developer.apple.com/help/account/membership/enrolling-in-the-app/

## 准备好的两个文件
- .github/workflows/jev-ios-testflight.yml：只有真实 Apple 签名配置齐备时才可能上传，且必须合并到默认分支后才可在 GitHub Actions 手动启动。
- release/prepare_jev_release.py：修改 App 与键盘两个 bundle ID、统一 App Group、设置手动签名、加入 UserDefaults 必需理由隐私清单；显示名改为「翼聊 AI / 翼聊键盘」。

## Apple 侧必须完成
1. 为主 App 和键盘扩展分别注册 explicit App ID（例如 com.example.wingchat、com.example.wingchat.keyboard）。
2. 注册单独 App Group（例如 group.com.example.wingchat），并将两个 App ID 都关联到它。
3. 创建 App Store Connect App、Apple Distribution 证书及两个 App Store provisioning profiles。
4. 创建 App Store Connect API Key，安全配置 GitHub Actions 里的机密项目。
5. 从 GitHub Actions 手动启动 TestFlight signed release workflow，等待 Apple 处理成功。
6. 在 App Store Connect → TestFlight 分配测试组、邀请测试员；外部测试可能先需 Apple Beta App Review。此时才有真实邀请邮件或公开链接。

## GitHub Actions 配置项
**Variables**（非密钥）
- ZW_APP_BUNDLE_ID
- ZW_APP_GROUP_ID

**Secrets**（禁止发在聊天、Issue、公开源码中）
- APPLE_TEAM_ID
- APPLE_DISTRIBUTION_CERT_P12_B64
- APPLE_DISTRIBUTION_CERT_PASSWORD
- APPLE_APPSTORE_PROFILE_APP_B64
- APPLE_APPSTORE_PROFILE_KEYBOARD_B64
- ASC_API_KEY_P8_B64
- ASC_KEY_ID
- ASC_ISSUER_ID

使用名为 apple-testflight 的 GitHub Environment，建议启用人工审批。
证书/描述文件生成仍需要**开发者团队合法授权**，该工作流不是绕过 Apple 会员制度的工具。
只凭 iPhone 可以完成会员申请，但签名凭证的安全生成、上传配置仍要通过合法的云端 Mac 流程解决。

## 发行前仍须测试的内容
- 真机键盘切换、输入、剪贴板授权、App Group 数据共享。
- 外部模型的隐私处理。原项目在用户主动分析时，将复制的聊天消息发送到用户配置的第三方 AI 服务。
- App Store Connect 隐私标签、HTTPS 默认配置、审核说明。
- 原项目历史曾暴露过 API Key，旧密钥不得复用。
- 不能把无签名编译成功等同于可上架或者已有邀请码。

**现在的真实结果：构建与发布模板已备好；尚未 Apple 签名、上传或收到邀请码。**
