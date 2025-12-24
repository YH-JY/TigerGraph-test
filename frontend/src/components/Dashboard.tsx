import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Alert, Spin } from 'antd';
import { CloudServerOutlined, DatabaseOutlined, SafetyCertificateOutlined, BranchesOutlined } from '@ant-design/icons';
import { healthCheck, getStatistics } from '../services/api.ts';

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [healthStatus, setHealthStatus] = useState<any>(null);
  const [statistics, setStatistics] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const health = await healthCheck();
        setHealthStatus(health);

        const stats = await getStatistics();
        if (stats.status === 'success') {
          setStatistics(stats.data);
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      {healthStatus?.k8s && healthStatus.k8s.includes('error') && (
        <Alert
          message="Kubernetes 连接错误"
          description={healthStatus.k8s}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}
      
      {healthStatus?.tigergraph && healthStatus.tigergraph.includes('error') && (
        <Alert
          message="TigerGraph 连接错误"
          description={healthStatus.tigergraph}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Kubernetes 状态"
              value={healthStatus?.k8s === 'connected' ? '已连接' : '未连接'}
              valueStyle={{ 
                color: healthStatus?.k8s === 'connected' ? '#3f8600' : '#cf1322' 
              }}
              prefix={<CloudServerOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="TigerGraph 状态"
              value={healthStatus?.tigergraph === 'connected' ? '已连接' : '未连接'}
              valueStyle={{ 
                color: healthStatus?.tigergraph === 'connected' ? '#3f8600' : '#cf1322' 
              }}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总节点数"
              value={statistics?.vertexCount || 0}
              prefix={<SafetyCertificateOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总边数"
              value={statistics?.edgeCount || 0}
              prefix={<BranchesOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {statistics?.vertexTypes && (
        <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
          <Col span={24}>
            <Card title="资产类型分布">
              <Row gutter={[16, 16]}>
                {Object.entries(statistics.vertexTypes).map(([type, count]) => (
                  <Col xs={12} sm={8} md={6} key={type}>
                    <Statistic
                      title={type}
                      value={count as number}
                      className="stat-card"
                    />
                  </Col>
                ))}
              </Row>
            </Card>
          </Col>
        </Row>
      )}
    </div>
  );
};

export default Dashboard;