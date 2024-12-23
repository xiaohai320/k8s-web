<template>
    <div>
      <el-input v-model="name" placeholder="defalut"></el-input>
      <el-button plain type="primary"  @click="fetchData" >获取数据</el-button>
      <el-table :data="tableData" style="width: 100%" max-height="500">
      <el-table-column fixed prop="metadata.name" label="Node Name" width="200" />
        <el-table-column prop="metadata.creation_timestamp" label="Creation Time" width="150" />
        <!-- <el-table-column label="容器就绪" width="100">
          <template #default="scope">
            <span>{{ getContainerStatus(scope.row) }}</span>
          </template>
        </el-table-column> -->
        <el-table-column prop="status.phase" label="Node状态" width="120" />
        <el-table-column prop="status.host_ip" label="污点" width="120" />
        <el-table-column fixed="right" label="操作" width="120" align="center" >
          <template #default="scope">
            <el-button  type="warning" :icon="Edit" plain @click="handleCheck(scope.row)">Edit</el-button>
          </template>
      </el-table-column>    
      </el-table>
        <!-- 抽屉组件 -->
     
      <!-- 抽屉组件 -->
      <el-drawer
        title="Pod详情"
        v-model="drawerVisible"
        direction="rtl"
        size="50%"
      >
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
          <ul class="container-list">
            <li v-for="(container, index) in selectedPod.status.container_statuses" :key="index" class="container-item">
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
              <div class="container-detail">
                <span class="label">端口:</span>
                <span class="value">{{ container.ports ? container.ports.map(p => p.containerPort).join(', ') : '-' }}</span>
              </div>
              <div class="container-detail">
                <span class="label">环境变量:</span>
                <span class="value">{{ container.env ? container.env.map(e => `${e.name}=${e.value}`).join(', ') : '-' }}</span>
              </div>
            </li>
          </ul>
        </div>
      </el-drawer>
    </div>
    </template>
    <script lang="ts" setup>
    import { ref, onMounted } from 'vue';
    import axios from 'axios';
    import {
    Edit, Search
   
  } from '@element-plus/icons-vue'
    const drawerVisible = ref(false);
  
  // 选中的Pod
    const selectedPod:any = ref(null);
    const handleCheck = (pod: any) => {
      drawerVisible.value = true;
      selectedPod.value = pod;
     
    }
    const handleEdit = () => {
      console.log('Edit')
    }
  
    // 模拟数据
    const name = ref('');
    const tableData = ref([]);  
    // 获取数据的函数
    const fetchData = async () => {
      try {
        const params = { name: name.value };
        const response = await axios.get('http://127.0.0.1:5000/nodes', { params });
        tableData.value = response.data;
        console.log('Data fetched:', tableData);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
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
   </style>