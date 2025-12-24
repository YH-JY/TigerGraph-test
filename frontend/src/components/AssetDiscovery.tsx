import React, { useState } from 'react';
import { Button, Table, Tag, Tabs, message, Spin, Space, Alert } from 'antd';
import { SearchOutlined, ImportOutlined, ReloadOutlined } from '@ant-design/icons';
import { discoverAssets, importAssets } from '../services/api.ts';
import type { ColumnsType } from 'antd/es/table';

interface Asset {
  id: string;
  name: string;
  namespace?: string;
  status?: string;
  creation_time?: string;
  [key: string]: any;
}

const AssetDiscovery: React.FC = () => {
  const [assets, setAssets] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [importing, setImporting] = useState(false);

  const handleDiscover = async () => {
    setLoading(true);
    try {
      const result = await discoverAssets();
      setAssets(result.assets);
      message.success('资产发现成功');
    } catch (error: any) {
      message.error(`资产发现失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    setImporting(true);
    try {
      await importAssets();
      message.success('导入任务已启动，请稍后查看结果');
      
      // Poll for completion
      setTimeout(() => {
        setImporting(false);
      }, 5000);
    } catch (error: any) {
      message.error(`导入失败: ${error.message}`);
      setImporting(false);
    }
  };

  const renderTable = (data: Asset[], assetType: string) => {
    const columns: ColumnsType<Asset> = [
      {
        title: 'ID',
        dataIndex: 'id',
        key: 'id',
        width: '30%',
        ellipsis: true,
      },
      {
        title: '名称',
        dataIndex: 'name',
        key: 'name',
        width: '20%',
      },
      {
        title: '命名空间',
        dataIndex: 'namespace',
        key: 'namespace',
        width: '15%',
        render: (ns: string) => ns ? <Tag color="blue">{ns}</Tag> : '-',
      },
      {
        title: '状态',
        dataIndex: 'status',
        key: 'status',
        width: '15%',
        render: (status: string) => {
          let color = 'default';
          if (status === 'Running') color = 'green';
          else if (status === 'Pending') color = 'orange';
          else if (status === 'Failed') color = 'red';
          return <Tag color={color}>{status}</Tag>;
        },
      },
      {
        title: '创建时间',
        dataIndex: 'creation_time',
        key: 'creation_time',
        width: '20%',
        render: (time: string) => time ? new Date(time).toLocaleString() : '-',
      },
    ];

    return (
      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        size="small"
        scroll={{ x: 800 }}
      />
    );
  };

  const tabItems = assets ? [
    {
      key: 'namespaces',
      label: `命名空间 (${assets.namespaces?.length || 0})`,
      children: renderTable(assets.namespaces || [], 'Namespace'),
    },
    {
      key: 'nodes',
      label: `节点 (${assets.nodes?.length || 0})`,
      children: renderTable(assets.nodes || [], 'K8sNode'),
    },
    {
      key: 'pods',
      label: `Pods (${assets.pods?.length || 0})`,
      children: renderTable(assets.pods || [], 'Pod'),
    },
    {
      key: 'services',
      label: `服务 (${assets.services?.length || 0})`,
      children: renderTable(assets.services || [], 'Service'),
    },
    {
      key: 'deployments',
      label: `部署 (${assets.deployments?.length || 0})`,
      children: renderTable(assets.deployments || [], 'Deployment'),
    },
    {
      key: 'configmaps',
      label: `配置映射 (${assets.configmaps?.length || 0})`,
      children: renderTable(assets.configmaps || [], 'ConfigMap'),
    },
    {
      key: 'secrets',
      label: `密钥 (${assets.secrets?.length || 0})`,
      children: renderTable(assets.secrets || [], 'Secret'),
    },
    {
      key: 'rbac',
      label: `RBAC (${assets.rbac?.length || 0})`,
      children: renderTable(assets.rbac || [], 'RBAC'),
    },
  ] : [];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<SearchOutlined />}
          loading={loading}
          onClick={handleDiscover}
        >
          发现资产
        </Button>
        <Button
          icon={<ImportOutlined />}
          loading={importing}
          onClick={handleImport}
          disabled={!assets}
        >
          导入 TigerGraph
        </Button>
        <Button
          icon={<ReloadOutlined />}
          onClick={handleDiscover}
          disabled={!assets}
        >
          刷新
        </Button>
      </Space>

      {!assets && (
        <Alert
          message="尚未发现资产"
          description="点击'发现资产'按钮开始扫描 Kubernetes 集群"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" />
        </div>
      ) : assets ? (
        <Tabs items={tabItems} />
      ) : null}
    </div>
  );
};

export default AssetDiscovery;