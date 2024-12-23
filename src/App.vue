<template>
  <div class="common-layout">
    <el-container>
     <el-header> 
      <Webheader />
    </el-header>
      <el-container>
        <el-aside width="200px">
          <Left />
        </el-aside>
          <el-main class="content">
         <Breadcrumb />
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>  
import Left from '@/components/Left.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import Webheader from '@/components/Webheader.vue'

export default {
  name: 'App',
  components: {
    Left,
    Breadcrumb,
    Webheader
  }
}
const debounce = (fn, delay) => {
  let timer
   return (...args) => {
     if (timer) {
       clearTimeout(timer)
     }
     timer = setTimeout(() => {
       fn(...args)
     }, delay)
   }
}
const _ResizeObserver = window.ResizeObserver;
window.ResizeObserver = class ResizeObserver extends _ResizeObserver{
   constructor(callback) {
     callback = debounce(callback, 200);
     super(callback);
   }
}
</script>
<style>
*{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
.el-header {
  background-color: #ece3e3;
  color: #000000;
  height: 60px;
  line-height: 60px;
  padding: 0 20px;
}
.el-breadcrumb {
  margin:10px;
}
</style>
