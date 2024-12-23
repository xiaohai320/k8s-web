<template>
   
              <el-breadcrumb separator=">">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <template v-for="(item, index) in breadList">
              <el-breadcrumb-item
                v-if="item.name"
                :key="index"
                :to="item.path"
              >{
          { item.name }}</el-breadcrumb-item>
            </template>
            </el-breadcrumb>
          
  </template>
  <script>  

  </script>
 
  