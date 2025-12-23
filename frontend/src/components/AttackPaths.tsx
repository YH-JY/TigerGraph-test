import React, { useState, useEffect } from 'react';
import { Card, Select, Button, Table, Tag, Alert, Spin, Space, message } from 'antd';
import { SearchOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { queryAttackPaths, getAssetTypes } from '../services/api';
import type { ColumnsType } from 'antd/es/table';

interface AttackPath {
  id: string;
  source: string;
  target: string;
  risk_level: string;
  description: string;
}

const AttackPaths: React.FC = () => {
  const [assetTypes, setAssetTypes] = useState<any[]>([]);
  const [sourceType, setSourceType] = useState<string>('');
  const [targetType, setTargetType] = useState<string>('');
  const [attackPaths, setAttackPaths] = useState<AttackPath[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchAssetTypes = async () => {
      try {
        const types = await getAssetTypes();
        setAssetTypes(types.types);
      } catch (error: any) {
        message.error(`获取资产类型失败: ${error.message}`);
      }
    };
    fetchAssetTypes();
  }, []);

  const handleQuery = async () => {
    setLoading(true);
    try {
      const result = await queryAttackPaths({
        source_type: sourceType,
        target_type: targetType,
        max_depth: 5,
      });

      if (result.status === 'success' && result.data) {
        // Parse attack paths from TigerGraph result
        const paths: AttackPath[] = [];
        let id = 1;
        
        if (Array.isArray(result.data)) {
          result.data.forEach((item: any) => {
            if (item.paths) {
              item.paths.forEach((path: string) => {
                const riskLevel = path.includes('HIGH') ? 'high' : 
                                path.includes('MEDIUM') ? 'medium' : 'low';
                paths.push({
                  id: String(id++),
                  source: path.split(' -> ')[0],
                  target: path.split(' -> ')[1]?.split(' (')[0],
                  risk_level: riskLevel,
                  description: path,
                });
              });
            }
          });
        }
        
        setAttackPaths(paths);
        message.success(`发现 ${paths.length} 条潜在攻击路径`);
      } else {
        setAttackPaths([]);
        message.warning('未发现攻击路径');
      }
    } catch (error: any) {
      message.error(`查询失败: ${error.message}`);
      setAttackPaths([]);
    } finally {
      setLoading(false);
    }
  };

  const columns: ColumnsType<AttackPath> = [
    {
      title: '源资产类型',
      dataIndex: 'source',
      key: 'source',
      render: (text) => <Tag color="blue">{text}</Tag>,
    },
    {
      title: '目标资产类型',
      dataIndex: 'target',
      key: 'target',
      render: (text) => <Tag color="purple">{text}</Tag>,
    },
    {
      title: '风险等级',
      dataIndex: 'risk_level',
      key: 'risk_level',
      render: (level: string) => {
        let color = 'default';
        let text = '低';
        if (level === 'high') {
          color = 'red';
          text = '高';
        } else if (level === 'medium') {
          color = 'orange';
          text = '中';
        }
        return <Tag color={color}>{text}</Tag>;
      },
    },
    {
      title: '路径描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
  ];

  return (
    <div>
      <Card title="攻击路径分析" style={{ marginBottom: 16 }}>
        <Space>
          <Select
            placeholder="选择源资产类型"
            style={{ width: 200 }}
            value={sourceType}
            onChange={setSourceType}
            allowClear
          >
            {assetTypes.map((type) => (
              <Select.Option key={type.name} value={type.name}>
                {type.label}
              </Select.Option>
            ))}
          </Select>
          
          <Select
            placeholder="选择目标资产类型"
            style={{ width: 200 }}
            value={targetType}
            onChange={setTargetType}
            allowClear
          >
            {assetTypes.map((type) => (
              <Select.Option key={type.name} value={type.name}>
                {type.label}
              </Select.Option>
            ))}
          </Select>
          
          <Button
            type="primary"
            icon={<SearchOutlined />}
            onClick={handleQuery}
            loading={loading}
          >
            查询攻击路径
          </Button>
        </Space>
      </Card>

      {attackPaths.length === 0 && !loading && (
        <Alert
          message="暂无攻击路径数据"
          description="请选择源和目标资产类型，然后点击'查询攻击路径'按钮"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" />
        </div>
      ) : attackPaths.length > 0 ? (
        <Card title={`发现 ${attackPaths.length} 条潜在攻击路径`}>
          <Table
            columns={columns}
            dataSource={attackPaths}
            rowKey="id"
            pagination={{
              pageSize: 10,
            }}
          />
          
          <Alert
            message="攻击路径风险说明"
            description={
              <div>
                <p><Tag color="red">高风险</Tag>：直接访问敏感资源，如密钥、RBAC权限等</p>
                <p><Tag color="orange">中风险</Tag>：需要跳转才能到达敏感资源的路径</p>
                <p><Tag color="green">低风险</Tag>：常规的资源访问路径</p>
              </div>
            }
            type="warning"
            showIcon
            icon={<ExclamationCircleOutlined />}
            style={{ marginTop: 16 }}
          />
        </Card>
      ) : null}
    </div>
  );
};

export default AttackPaths;