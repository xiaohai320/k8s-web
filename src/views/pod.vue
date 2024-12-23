<template>
  <div>
    <el-input v-model="namespace" placeholder="defalut"></el-input>
    <el-button plain type="primary" @click="fetchData">获取数据</el-button>
    <el-table :data="tableData" style="width: 100%" max-height="500">
      <el-table-column fixed prop="metadata.name" label="Pod Name" width="200" />
      <el-table-column prop="metadata.creation_timestamp" label="Creation Time" width="150" />
      <el-table-column prop="metadata.namespace" label="Namespace" width="120" />
      <el-table-column label="容器就绪" width="100">
        <template #default="scope">
          <span>{{ getContainerStatus(scope.row) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="status.phase" label="Pod状态" width="120" />
      <el-table-column prop="status.host_ip" label="Node_IP" width="120" />
      <el-table-column fixed="right" label="操作" width="120" align="center">
        <template #default="scope">
          <el-button type="warning" :icon="Edit" plain @click="handleEdit(scope.row)">Edit</el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- 抽屉组件 -->
    <el-drawer title="Pod详情" v-model="drawerVisible" @close="clearSvcdata" direction="rtl" size="50%">
      <div v-if="selectedPod" class="pod-details">
        <h3>基本信息</h3>
        <div class="detail-item">
          <span class="label">名称:</span>
          <span class="value">{{ selectedPod.metadata.name }}</span>
        </div>
        <div class="detail-item">
          <span class="label">命名空间:</span>
          <span class="value">{{ selectedPod.metadata.namespace }}</span>
        </div>
        <div class="detail-item">
          <span class="label">UID:</span>
          <span class="value">{{ selectedPod.metadata.uid }}</span>
        </div>
        <div class="detail-item">
          <span class="label">创建时间:</span>
          <span class="value">{{ selectedPod.metadata.creation_timestamp }}</span>
        </div>
        <div class="detail-item">
          <span class="label">状态:</span>
          <span class="value">{{ selectedPod.status.phase }}</span>
        </div>
        <h3>容器状态</h3>
        <el-tabs v-model="activeName" class="demo-tabs">
          <el-tab-pane label="Status" name="Status">
            <ul class="container-list">
              <li v-for="(container, index) in selectedPod.status.container_statuses" :key="index"
                class="container-item">
                <div class="container-detail">
                  <span class="label">名称:</span>
                  <span class="value">{{ container.name }}</span>
                </div>
                <div class="container-detail">
                  <span class="label">镜像:</span>
                  <span class="value">{{ container.image }}</span>
                </div>
                <div class="container-detail">
                  <span class="label">就绪:</span>
                  <span class="value">{{ container.ready ? '是' : '否' }}</span>
                </div>
                <div class="container-detail">
                  <span class="label">重启次数:</span>
                  <span class="value">{{ container.restart_count }}</span>
                </div>
                <div class="container-detail">
                  <span class="label">启动时间:</span>
                  <span class="value">{{ container.state.running?.started_at }}</span>
                </div>
              </li>
            </ul>
          </el-tab-pane>
          <el-tab-pane label="Volume" name="Volume">
            <ul class="container-list">
              <li v-for="(container, index) in selectedPod.spec.containers" :key="index" class="container-item">
                <div class="container-detail">
                  <span class="label" style="width: 200px;">{{ container.name }}挂载:</span>
                  <span class="value">{{ container.volume_mounts ? container.volume_mounts.map(e =>
                    `${e.name}=${e.value}`).join(', ') : '-' }}</span>
                </div>
              </li>
            </ul>
          </el-tab-pane>
          <el-tab-pane label="Network" name="Network">
            <el-table :data="svcdata" style="width: 100%" max-height="500">
              <el-table-column prop="metadata.name" label="container_name" width="200" />
              <el-table-column prop="spec.cluster_ip" label="cluster_ip" width="120" />
              <el-table-column prop="spec.type" label="Type" width="100" />
              <el-table-column label="Ports" width="100">
                <template #default="scope">
                  <el-button type="text" @click="handleRowClick(scope.row)">View Ports</el-button>
                </template>

              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="ENV" name="ENV">
            <ul class="container-list">
              <li v-for="(container, index) in selectedPod.spec.containers" :key="index" class="container-item">
                <div class="container-detail">
                  <span class="label" style="width: 200px;">{{ container.name }}环境变量:</span>
                  <span class="value">{{ container.env ? container.env.map(e => `${e.name}=${e.value}`).join(', ') : '-'
                    }}</span>
                </div>
              </li>
            </ul>
          </el-tab-pane>
        </el-tabs>
        <el-dialog v-model="dialogTableVisible" title="Ports Details" width="800" custom-class="custom-dialog">
      <div v-if="selectedRow" class="dialog-content">
        <el-row :gutter="20">
          <el-col :span="24" v-for="(port, index) in selectedRow.spec.ports" :key="index" class="port-item">
            <el-card shadow="hover" class="port-card">
              <div class="port-header">
                <span>Port {{ port.name }}:</span>
              </div>
              <el-row :gutter="10">
                <el-col :span="6">
                  <strong>Node Port:</strong> {{ port.node_port }}
                </el-col>
                <el-col :span="6">
                  <strong>Port:</strong> {{ port.port }}
                </el-col>
                <el-col :span="6">
                  <strong>Protocol:</strong> {{ port.protocol }}
                </el-col>
                <el-col :span="6">
                  <strong>Target Port:</strong> {{ port.target_port }}
                </el-col>
              </el-row>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
      </div>
    </el-drawer>
  </div>
</template>
<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import {
  Edit, Search
} from '@element-plus/icons-vue'
import { TabsPaneContext } from 'element-plus';
import { da } from 'element-plus/es/locale';
const activeName = ref('Status')
const svcdata: any = ref([]);
const dialogTableVisible = ref(false);
const drawerVisible = ref(false);
// 模拟数据
const namespace = ref('');
const tableData = ref([]);
// 选中的Pod
const selectedPod: any = ref(null);
const selectedRow: any = ref(null);
const handleEdit = (pod: any) => {

  drawerVisible.value = true;
  selectedPod.value = pod;
  // console.log("Selected pod1:", pod.metadata.labels);
  // console.log("Selected pod2:", selectedPod.value.metadata.labels);
  getsvc(selectedPod.value.metadata.namespace, selectedPod.value.metadata.labels)
}

const getsvc = async (namespace: any, label: any) => {
  try {
    const params = { label: label, namespace: namespace }
    console.log("params:", params);
    const response = await axios.get('http://127.0.0.1:5000/svc', { params });
    svcdata.value = response.data;
    console.log("SVC Status:", response.data);
    return response.data;

  } catch (error: any) {
    throw new Error(error.response ? error.response.data.error : '网络请求失败');
  }
}
// 获取数据的函数
const fetchData = async () => {
  try {
    const params = { namespace: namespace.value };
    const response = await axios.get('http://127.0.0.1:5000/pods', { params });
    tableData.value = response.data;
    console.log("Table Data:", tableData.value);
  } catch (error) {
    console.error('Error fetching data:', error);
  }
};
const getContainerStatus = (pod: { status: { container_statuses: any; }; }) => {
  const containerStatuses = pod.status.container_statuses;
  if (containerStatuses) {
    const readyCount = containerStatuses.filter((status: { ready: any; }) => status.ready).length;
    return `${readyCount}/${containerStatuses.length}`;
  }
  return 'N/A';
};
const clearSvcdata = () => {
  svcdata.value = [];
  console.log("Clear Svcdata");
};
const handleRowClick = (row:any) => {
  selectedRow.value = row;
  console.log("Selected Row:", row);
  dialogTableVisible.value = true;
};
</script>


<style scoped>
.data-display {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.common-layout {
  height: 100vh;
  background-color: #f0f2f5;
}

.el-header {
  background-color: #409eff;
  color: #fff;
  text-align: center;
  line-height: 60px;
  font-size: 24px;
  font-weight: bold;
}

.el-aside {
  background-color: #d3dce6;
  color: #333;
  text-align: center;
  line-height: 200px;
}

.content {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.el-breadcrumb {
  margin-bottom: 20px;
  font-size: 16px;
  color: #606266;
}

.el-table {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.el-table th {
  background-color: #f5f7fa;
  color: #909399;
  font-weight: normal;
  text-align: left;
}

.el-table td {
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}


.pod-details {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.pod-details h3 {
  margin-top: 0;
  font-size: 18px;
  color: #333;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.detail-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  font-size: 14px;
}

.label {
  width: 100px;
  font-weight: bold;
  color: #606266;
}

.value {
  flex: 1;
  color: #303133;
}

.container-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.container-item {
  border-bottom: 1px solid #e4e7ed;
  padding: 10px 0;
  margin-bottom: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.container-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.container-detail {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
  font-size: 14px;
  
}

.container-detail .label {
  width: 100px;
  font-weight: bold;
  color: #606266;
}

.container-detail .value {
  flex: 1;
  color: #303133;
}
.port-header {
 
  background-color: #f0f2f5;
  border-bottom: 1px solid #ccb9b9;
  margin-bottom: 10px;
}
</style>