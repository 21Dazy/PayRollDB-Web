// 导出所有store
export { useAuthStore } from './auth';
export { useUsersStore } from './users';
export { useDepartmentsStore } from './departments';
export { usePositionsStore } from './positions';
export { useEmployeesStore } from './employees';
export { useAttendanceStore } from './attendance';
export { useSalariesStore } from './salaries';
export { useSocialSecurityStore } from './social-security';
export { useSystemStore } from './system';

// 导出API服务
export { default as request, get, post, put, del } from '@/utils/request'; 