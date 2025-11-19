/**
 * NetworkGraph Component (Phase 4 - Step 8)
 * React Flow based network visualization
 */

import { useMemo, useCallback } from 'react'
import {
  ReactFlow,
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  ConnectionLineType,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import type { GraphData } from '@/types/graph'
import dagre from 'dagre'

interface NetworkGraphProps {
  data: GraphData
  onNodeClick?: (nodeId: string) => void
}

// Layout algorithm using dagre
const getLayoutedElements = (nodes: Node[], edges: Edge[]) => {
  const dagreGraph = new dagre.graphlib.Graph()
  dagreGraph.setDefaultEdgeLabel(() => ({}))
  dagreGraph.setGraph({ rankdir: 'TB', nodesep: 100, ranksep: 150 })

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 100, height: 100 })
  })

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target)
  })

  dagre.layout(dagreGraph)

  return {
    nodes: nodes.map((node) => {
      const nodeWithPosition = dagreGraph.node(node.id)
      return {
        ...node,
        position: {
          x: nodeWithPosition.x,
          y: nodeWithPosition.y,
        },
      }
    }),
    edges,
  }
}

export const NetworkGraph: React.FC<NetworkGraphProps> = ({ data, onNodeClick }) => {
  // Convert GraphData to React Flow format
  const initialNodes: Node[] = useMemo(() => {
    return data.nodes.map((node) => ({
      id: node.id,
      type: node.type === 'author' ? 'default' : 'default',
      position: { x: 0, y: 0 },
      data: {
        label: node.label,
      },
      style: {
        backgroundColor: node.type === 'author' ? '#4F46E5' : '#10B981',
        color: 'white',
        border: '2px solid #312E81',
        borderRadius: node.type === 'author' ? '50%' : '8px',
        width: Math.max(60, node.size / 3),
        height: Math.max(60, node.size / 3),
        fontSize: '10px',
        fontWeight: 'bold',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '4px',
      },
    }))
  }, [data.nodes])

  const initialEdges: Edge[] = useMemo(() => {
    return data.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: ConnectionLineType.Straight,
      style: {
        strokeWidth: Math.max(1, edge.weight / 2),
        stroke: edge.type === 'coauthorship' ? '#94A3B8' : '#6EE7B7',
      },
      label: edge.weight > 1 ? `${edge.weight}` : undefined,
      labelStyle: {
        fontSize: '10px',
        fill: '#64748B',
      },
    }))
  }, [data.edges])

  // Apply layout
  const { nodes: layoutedNodes, edges: layoutedEdges } = useMemo(() => {
    return getLayoutedElements(initialNodes, initialEdges)
  }, [initialNodes, initialEdges])

  const [nodes, , onNodesChange] = useNodesState(layoutedNodes)
  const [edges, , onEdgesChange] = useEdgesState(layoutedEdges)

  const handleNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      if (onNodeClick) {
        onNodeClick(node.id)
      }
    },
    [onNodeClick]
  )

  return (
    <div style={{ width: '100%', height: '700px', backgroundColor: '#F9FAFB' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        fitView
        minZoom={0.1}
        maxZoom={2}
        attributionPosition="bottom-left"
      >
        <Background color="#E2E8F0" gap={16} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            const bgColor = node.style?.backgroundColor as string
            return bgColor || '#4F46E5'
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
        />
      </ReactFlow>
    </div>
  )
}
