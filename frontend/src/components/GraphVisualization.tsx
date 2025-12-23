import React, { useState, useEffect } from 'react';
import { Card, Button, Select, Switch, message, Spin, Space, Row, Col } from 'antd';
import { ReloadOutlined, FullscreenOutlined } from '@ant-design/icons';
import CytoscapeComponent from 'react-cytoscapejs';
import { getGraphVisualization } from '../services/api';

const GraphVisualization: React.FC = () => {
  const [graphData, setGraphData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [layout, setLayout] = useState<string>('cose');
  const [showLabels, setShowLabels] = useState(true);

  const vertexColors: { [key: string]: string } = {
    K8sNode: '#1890ff',
    Pod: '#52c41a',
    Service: '#faad14',
    Deployment: '#722ed1',
    ConfigMap: '#fa8c16',
    Secret: '#ff4d4f',
    Namespace: '#13c2c2',
    RBAC: '#eb2f96',
    Container: '#2f54eb',
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const result = await getGraphVisualization();
      if (result.status === 'success' && result.data) {
        // Transform data for Cytoscape
        const cytoscapeData = {
          elements: [],
        };

        // Add vertices
        if (result.data.vertices) {
          result.data.vertices.forEach((vertex: any) => {
            cytoscapeData.elements.push({
              data: {
                id: vertex.v_id,
                label: vertex.attributes.name || vertex.v_id,
                type: vertex.v_type,
                color: vertexColors[vertex.v_type] || '#666',
              },
            });
          });
        }

        // Add edges
        if (result.data.edges) {
          result.data.edges.forEach((edge: any) => {
            cytoscapeData.elements.push({
              data: {
                id: `${edge.from_type}_${edge.from_id}_${edge.to_type}_${edge.to_id}`,
                source: edge.from_id,
                target: edge.to_id,
                label: edge.e_type,
                type: edge.e_type,
              },
            });
          });
        }

        setGraphData(cytoscapeData);
        message.success('图谱数据加载成功');
      } else {
        message.warning('请先执行资产发现和导入操作');
      }
    } catch (error: any) {
      message.error(`加载失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const stylesheet = [
    {
      selector: 'node',
      style: {
        backgroundColor: 'data(color)',
        label: showLabels ? 'data(label)' : '',
        textValign: 'center',
        textHalign: 'center',
        color: 'white',
        fontSize: '10px',
        width: '40px',
        height: '40px',
      },
    },
    {
      selector: 'edge',
      style: {
        label: showLabels ? 'data(label)' : '',
        width: 2,
        lineColor: '#ccc',
        targetArrowColor: '#ccc',
        targetArrowShape: 'triangle',
        curveStyle: 'bezier',
        fontSize: '8px',
        color: '#666',
      },
    },
    {
      selector: 'node:selected',
      style: {
        borderWidth: 3,
        borderColor: '#ff4d4f',
      },
    },
    {
      selector: 'edge:selected',
      style: {
        width: 4,
        lineColor: '#ff4d4f',
        targetArrowColor: '#ff4d4f',
      },
    },
  ];

  const layoutOptions = {
    name: layout,
    animate: true,
    fit: true,
    padding: 50,
    spacingFactor: 1.5,
    nodeDimensionsIncludeLabels: true,
  };

  const legendItems = Object.entries(vertexColors).map(([type, color]) => ({
    type,
    color,
    label: {
      K8sNode: '节点',
      Pod: 'Pod',
      Service: '服务',
      Deployment: '部署',
      ConfigMap: '配置',
      Secret: '密钥',
      Namespace: '命名空间',
      RBAC: '权限',
      Container: '容器',
    }[type] || type,
  }));

  return (
    <div>
      <Card title="云原生资产图谱" style={{ marginBottom: 16 }}>
        <Space wrap>
          <Button
            icon={<ReloadOutlined />}
            onClick={loadData}
            loading={loading}
          >
            刷新数据
          </Button>
          
          <Select
            value={layout}
            onChange={setLayout}
            style={{ width: 150 }}
            options={[
              { value: 'cose', label: '力导向布局' },
              { value: 'circle', label: '圆形布局' },
              { value: 'grid', label: '网格布局' },
              { value: 'breadthfirst', label: '层次布局' },
              { value: 'concentric', label: '同心圆布局' },
            ]}
          />
          
          <Switch
            checked={showLabels}
            onChange={setShowLabels}
            checkedChildren="显示标签"
            unCheckedChildren="隐藏标签"
          />
        </Space>
      </Card>

      <Row gutter={[16, 16]}>
        <Col span={20}>
          <Card>
            {loading ? (
              <div style={{ height: 600, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Spin size="large" />
              </div>
            ) : graphData ? (
              <div style={{ height: 600 }}>
                <CytoscapeComponent
                  elements={graphData.elements}
                  style={{ width: '100%', height: '100%' }}
                  layout={layoutOptions}
                  stylesheet={stylesheet}
                />
              </div>
            ) : (
              <div style={{ height: 600, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                暂无数据
              </div>
            )}
          </Card>
        </Col>
        <Col span={4}>
          <Card title="图例" size="small">
            {legendItems.map((item) => (
              <div key={item.type} style={{ marginBottom: 8, display: 'flex', alignItems: 'center' }}>
                <div
                  style={{
                    width: 20,
                    height: 20,
                    backgroundColor: item.color,
                    marginRight: 8,
                    borderRadius: '50%',
                  }}
                />
                <span>{item.label}</span>
              </div>
            ))}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default GraphVisualization;