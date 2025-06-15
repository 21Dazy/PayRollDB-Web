<template>
  <div class="salary-item">
    <div class="page-header">
      <h2>薪资项目管理</h2>
      <div class="page-actions">
        <el-button type="primary" :icon="Plus" @click="handleAdd">添加项目</el-button>
      </div>
    </div>
    
    <div class="data-table">
      <el-table
        :data="tableData"
        style="width: 100%"
        border
        stripe
        v-loading="loading"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="项目名称" width="150" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.type === 'addition' ? 'success' : 'danger'">
              {{ row.type === 'addition' ? '收入项' : '扣减项' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_percentage" label="计算方式" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_percentage ? 'warning' : 'info'">
              {{ row.is_percentage ? '百分比' : '固定金额' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_system" label="系统项" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_system ? 'primary' : ''">
              {{ row.is_system ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button 
              link 
              type="primary" 
              size="small" 
              @click="handleEdit(row)"
              :disabled="row.is_system"
            >
              编辑
            </el-button>
            <el-button 
              link 
              type="danger" 
              size="small" 
              @click="handleDelete(row)"
              :disabled="row.is_system"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑薪资项目' : '添加薪资项目'"
      width="500px"
    >
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="100px"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择项目类型" style="width: 100%" @change="$forceUpdate()">
            <el-option label="收入项" value="addition" />
            <el-option label="扣减项" value="deduction" />
          </el-select>
        </el-form-item>
        <el-form-item label="计算方式" prop="is_percentage">
          <el-radio-group v-model="form.is_percentage">
            <el-radio :label="false">固定金额</el-radio>
            <el-radio :label="true">百分比</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">确认</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import type { FormInstance } from 'element-plus';
import { useSalaryItemsStore } from '@/stores/salaryItems';

// 状态
const salaryItemsStore = useSalaryItemsStore();
const loading = ref(false);
const dialogVisible = ref(false);
const isEdit = ref(false);
const submitting = ref(false);
const currentId = ref<number | null>(null);
const formRef = ref<FormInstance | null>(null);

// 表格数据
const tableData = ref([]);

// 表单数据
const form = reactive({
  name: '',
  type: 'addition',
  is_percentage: false
});

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择项目类型', trigger: 'change' }
  ]
};

// 获取薪资项目列表
const fetchSalaryItems = async () => {
  loading.value = true;
  try {
    const data = await salaryItemsStore.getSalaryItems();
    tableData.value = data;
  } catch (error) {
    console.error('获取薪资项目失败:', error);
    ElMessage.error('获取薪资项目失败');
  } finally {
    loading.value = false;
  }
};

// 添加薪资项目
const handleAdd = () => {
  resetForm();
  isEdit.value = false;
  dialogVisible.value = true;
};

// 编辑薪资项目
const handleEdit = (row) => {
  resetForm();
  isEdit.value = true;
  currentId.value = row.id;
  
  // 填充表单数据
  form.name = row.name;
  form.type = row.type;
  form.is_percentage = row.is_percentage;
  
  dialogVisible.value = true;
};

// 删除薪资项目
const handleDelete = (row) => {
  if (row.is_system) {
    ElMessage.warning('系统项目不可删除');
    return;
  }
  
  ElMessageBox.confirm(
    `确定要删除薪资项目"${row.name}"吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await salaryItemsStore.deleteSalaryItem(row.id);
      ElMessage.success('删除成功');
      fetchSalaryItems();
    } catch (error) {
      console.error('删除薪资项目失败:', error);
      ElMessage.error('删除薪资项目失败');
    }
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
};

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return;
  
  try {
    await formRef.value.validate();
    
    submitting.value = true;
    
    if (isEdit.value && currentId.value) {
      // 更新薪资项目
      await salaryItemsStore.updateSalaryItem(currentId.value, form);
      ElMessage.success('更新成功');
    } else {
      // 创建薪资项目
      await salaryItemsStore.createSalaryItem(form);
      ElMessage.success('创建成功');
    }
    
    dialogVisible.value = false;
    fetchSalaryItems();
  } catch (error) {
    console.error('保存薪资项目失败:', error);
    ElMessage.error('保存失败');
  } finally {
    submitting.value = false;
  }
};

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields();
  }
  
  form.name = '';
  form.type = 'addition';
  form.is_percentage = false;
  currentId.value = null;
};

// 初始化
onMounted(() => {
  fetchSalaryItems();
});
</script>

<style scoped lang="scss">
.salary-item {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h2 {
      font-size: 20px;
      font-weight: 600;
      margin: 0;
    }
    
    .page-actions {
      display: flex;
      gap: 10px;
    }
  }
  
  .data-table {
    background-color: #fff;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.04);
    margin-bottom: 20px;
  }
}
</style> 