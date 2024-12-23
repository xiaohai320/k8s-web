<template>
  <div>
    <el-input v-model="namespace" placeholder="defalut"></el-input>
    <el-button plain type="primary" @click="fetchData">获取数据</el-button>
    <el-table :data="tableData" style="width: 100%" max-height="500">
      <el-table-column fixed prop="metadata.name" label="Deployment Name" width="200" />
      <el-table-column prop="metadata.creation_timestamp" label="Creation Time" width="150" />
      <el-table-column prop="metadata.namespace" label="Namespace" width="120" />
      <el-table-column label="副本数量" width="120">
        <template #default="scope">
          <template v-if="scope.$cellIndex == cellIndex && scope.$index == index">
            <div class="changebox">
            <el-input v-model="tempReplicas" />
            <el-button  plain link :icon="Close" @click="cancelEvent"></el-button>
            <el-button plain link :icon="Check" @click="confirmEvent(scope.row)"></el-button>
            </div>
          </template>
          <template v-else>
            <el-button
              @click="editReplicas(scope.row, scope.$index)">{{ scope.row.status.ready_replicas || 0}} /{{ scope.row.status.replicas }}</el-button>
          </template>
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="120" align="center">
        <template #default="scope">
          <el-button type="warning" :icon="Edit" plain @click="handleCheck(scope.row)">Edit</el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- 抽屉组件 -->
    <el-drawer title="Deployment详情" v-model="drawerVisible" direction="rtl" size="50%">
      <div v-if="selectedDeployment" class="deployment-details">
        <h3>基本信息</h3>
        <div class="detail-item">
          <span class="label">名称:</span>
          <span class="value">{{ selectedDeployment.metadata.name }}</span>
        </div>
        <div class="detail-item">
          <span class="label">命名空间:</span>
          <span class="value">{{ selectedDeployment.metadata.namespace }}</span>
        </div>
        <div class="detail-item">
          <span class="label">UID:</span>
          <span class="value">{{ selectedDeployment.metadata.uid }}</span>
        </div>
        <div class="detail-item">
          <span class="label">创建时间:</span>
          <span class="value">{{ selectedDeployment.metadata.creationTimestamp }}</span>
        </div>
        <div class="detail-item">
          <span class="label">当前副本数:</span>
          <span class="value">{{ selectedDeployment.spec.replicas }}</span>
        </div>
        <h3>容器状态</h3>
        <ul class="container-list">
          <li v-for="(container, index) in selectedDeployment.spec.template.spec.containers" :key="index"
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
              <span class="label">端口:</span>
              <span class="value">{{ container.ports ? container.ports.map(p => p.containerPort).join(', ') : '-'
                }}</span>
            </div>
            <div class="container-detail">
              <span class="label">环境变量:</span>
              <span class="value">{{ container.env ? container.env.map(e => `${e.name}=${e.value}`).join(', ') : '-'
                }}</span>
            </div>
          </li>
        </ul>
      </div>
    </el-drawer>
  </div>
</template>
<script lang="ts" setup>
import { ref } from 'vue';
import axios from 'axios';
import {
  Edit, 
  Close,
  Check
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus';
const drawerVisible = ref(false);
const cellIndex = ref('')
const index = ref('')
const tempReplicas = ref('');

// 选中的Pod
const selectedDeployment: any = ref(null);
const handleCheck = (pod: any) => {
  drawerVisible.value = true;
  selectedDeployment.value = pod;

}
const editReplicas = (row: any, ind: any) => {
  cellIndex.value = row.cellIndex
  index.value = ind
  tempReplicas.value = row.status.ready_replicas;
};
// 模拟数据
const namespace = ref('');
const tableData: any = ref([]);
// 获取数据的函数
const fetchData = async () => {
  try {
    const params = { namespace: namespace.value };
    const response = await axios.get('http://127.0.0.1:5000/deployments', { params });
    tableData.value = response.data;
    console.log('Data fetched:', tableData.value[0]);
  } catch (error) {
    console.error('Error fetching data:', error);
  }
};

// 保存副本数
const confirmEvent=(row: any)=>{
  let tempindex: any = ref('')
  tempindex = index.value
  cellIndex.value = ''
  index.value = ''
  const newReplicas = parseInt(tempReplicas.value, 10);
  if (isNaN(newReplicas) || newReplicas <= 0) {
    ElMessage({
    message: '请输入有效的正整数',
    type: 'warning',
  })
    return;
  }
  if (confirm(`是否将副本数修改为: ${newReplicas}?`)) {
    // 调用API进行实际的扩缩容操作
    scalePods(row.metadata.namespace, row.metadata.name, newReplicas)
      .then((data1) => {
        console.log(data1)
        ElMessage({
        message: '副本数修改成功',
        type: 'success',
        })
        setTimeout(()=>{
          fetchRowData( row.metadata.namespace, row.metadata.name)
          .then(data => {
            console.log(data)
            tableData.value[tempindex] = data;
            ElMessage({
           message: '数据刷新成功',
            type: 'success',
            })
              })
          .catch(error => {
          ElMessage({
          message: '获取副本数失败:'+error,
          type: 'error',
         })
          })
        },500)
       
      })
      .catch(error => {
        ElMessage({
          message: '副本数修改失败:'+error,
          type: 'error',
         })
      });
  } else {
    
  }

 }
const cancelEvent=()=>{
  cellIndex.value=''
  index.value=''

}
// 重新获取某一行的数据
const fetchRowData = async (namespace: any, deploymentName: any) => {
  try {
    const response = await axios.get(`http://127.0.0.1:5000/deployments/${namespace}/${deploymentName}`);
    return response.data;
  } catch (error: any) {
    throw new Error(error.response ? error.response.data.error : '网络请求失败');
  }
};


// 调用API进行扩缩容操作
const scalePods = async (namespace: any, deploymentName: any, replicas: number) => {
  try {
    const response = await axios.post('http://localhost:5000/scale-pods', {
      deployment_name: deploymentName,
      replicas: replicas,
      namespace: namespace
    });
    return response.data;
  } catch (error: any) {
    throw new Error(error.response ? error.response.data.error : '网络请求失败');
  }
};
</script>


<style scoped>
.changebox{
  display: flex;
  align-items: center; /* 垂直居中对齐 */
  gap: 2px; /* 元素之间的间距 */
  .el-input{
    width: 50px;
  }
}
.changebox  > :nth-child(2){
      width: 15px;height: 15px;
      background-color: #a7a7a76e;
      color: #ff0000;
  }
 .changebox > :nth-child(3){
    width: 15px;height: 15px;
    background-color: #a7a7a770;
    color: #2b9601;
  }
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

</style>