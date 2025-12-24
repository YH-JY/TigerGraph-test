import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout, Menu, Typography, theme } from 'antd';
import {
  DashboardOutlined,
  CloudServerOutlined,
  ShareAltOutlined,
  SettingOutlined
} from '@ant-design/icons';
import Dashboard from './components/Dashboard.tsx';
import AssetDiscovery from './components/AssetDiscovery.tsx';
import AttackPaths from './components/AttackPaths.tsx';
import GraphVisualization from './components/GraphVisualization.tsx';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

const App: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '仪表板',
    },
    {
      key: '/discovery',
      icon: <CloudServerOutlined />,
      label: '资产发现',
    },
    {
      key: '/attack-paths',
      icon: <ShareAltOutlined />,
      label: '攻击路径',
    },
    {
      key: '/graph',
      icon: <SettingOutlined />,
      label: '图谱可视化',
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div className="logo">
          {collapsed ? 'K8S' : 'K8S Security'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          defaultSelectedKeys={['/']}
          items={menuItems}
          onClick={({ key }) => {
            window.location.hash = key;
          }}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: 0, background: colorBgContainer }}>
          <Title level={3} style={{ margin: '0 24px', padding: '12px 0' }}>
            Kubernetes 原生安全平台
          </Title>
        </Header>
        <Content style={{ margin: '24px 16px', padding: 24, background: colorBgContainer }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/discovery" element={<AssetDiscovery />} />
            <Route path="/attack-paths" element={<AttackPaths />} />
            <Route path="/graph" element={<GraphVisualization />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};

export default App;