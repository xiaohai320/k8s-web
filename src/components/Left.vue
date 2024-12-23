<template>
    <el-row class="tac">
        <el-col>
            <el-menu default-active="1" class="el-menu-vertical-demo" @open="handleOpen" router="true"
                @close="handleClose">
                <el-sub-menu index="1">
                    <template #title>
                        <el-icon>
                            <location />
                        </el-icon>
                        <span>集群管理</span>
                    </template>
                    <el-menu-item-group>
                        <el-menu-item index="pod">集群Pod状态</el-menu-item>
                        <el-menu-item index="deployment">集群Deployment状态</el-menu-item>
                        <el-menu-item index="node">集群Node状态</el-menu-item>
                    </el-menu-item-group>
                    
                </el-sub-menu>

                <el-menu-item index="yidong">
                    <el-icon>
                    </el-icon>
                    <span>集群日志</span>
                </el-menu-item>
                <el-menu-item index="log">
                    <el-icon>
                    </el-icon>
                    <span>异动管理</span>
                </el-menu-item>
                <el-menu-item index="views">
                    <el-icon>
         
                    </el-icon>
                    <span>指标看板</span>
                </el-menu-item>
                <el-menu-item index="userinfo">
                    <el-icon>
                 
                    </el-icon>
                    <span>用户设置</span>
                </el-menu-item>
            </el-menu>
        </el-col>
    </el-row>
</template>

<script lang="ts" setup>


// const handleOpen = (key: string, keyPath: string[]) => {
//     // console.log(key, keyPath)
// }
// const handleClose = (key: string, keyPath: string[]) => {
//     // console.log(key, keyPath)
// }
</script>
<style lang="scss" scoped></style>