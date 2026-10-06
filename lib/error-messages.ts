const ERROR_MESSAGES: Record<string, string> = {
  INVALID_INPUT: 'Dữ liệu nhập chưa hợp lệ.',
  INVALID_TOKEN: 'Vui lòng nhập mã hội viên hoặc mã QR.',
  INVALID_QR: 'Không tìm thấy mã hội viên.',
  MEMBER_INACTIVE: 'Hội viên đã ngừng hoạt động.',
  MEMBER_NOT_ACTIVE: 'Hội viên không tồn tại hoặc đã ngừng hoạt động.',
  MEMBER_NOT_FOUND: 'Không tìm thấy hội viên.',
  DUPLICATE_MEMBER: 'Số điện thoại hoặc email đã thuộc một hội viên khác.',
  DUPLICATE_DATA: 'Dữ liệu này đã tồn tại trong hệ thống.',
  DUPLICATE_USERNAME: 'Tên đăng nhập đã được sử dụng.',
  ALREADY_LINKED: 'Hội viên đã có tài khoản đăng nhập.',
  EMAIL_REQUIRED: 'Hội viên cần có email trước khi gửi lời mời.',
  PLAN_NOT_FOUND: 'Gói tập không tồn tại hoặc đã ngừng bán.',
  OVERLAPPING_SUBSCRIPTION: 'Thời gian gói mới bị chồng lấn với gói hiện có.',
  SUBSCRIPTION_FROZEN: 'Gói tập đang được đóng băng.',
  SUBSCRIPTION_NOT_STARTED: 'Gói tập chưa đến ngày bắt đầu.',
  SUBSCRIPTION_EXPIRED: 'Gói tập đã hết hạn.',
  NO_VALID_SUBSCRIPTION: 'Không có gói tập còn hiệu lực.',
  NO_VISITS_LEFT: 'Gói tập đã hết lượt.',
  DUPLICATE: 'Hội viên đã check-in trong 10 phút gần nhất.',
  INVALID_FREEZE: 'Ngày hoặc lý do đóng băng chưa hợp lệ.',
  ALREADY_FROZEN: 'Gói tập đang có một kỳ đóng băng.',
  NOT_FROZEN: 'Gói tập hiện không bị đóng băng.',
  REASON_REQUIRED: 'Vui lòng nhập lý do thực hiện thao tác.',
  PAYMENT_NOT_FOUND: 'Không tìm thấy giao dịch hợp lệ.',
  LAST_MANAGER: 'Không thể khóa hoặc hạ quyền quản lý cuối cùng.',
  CANNOT_CHANGE_SELF:
    'Bạn không thể khóa hoặc hạ quyền tài khoản của chính mình.',
  INVALID_ASSIGNEE: 'Người phụ trách không tồn tại hoặc đã ngừng hoạt động.',
  PAST_CONTACT_TIME: 'Thời gian chăm sóc không được ở trong quá khứ.',
  UNAUTHENTICATED: 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.',
  FORBIDDEN: 'Bạn không có quyền thực hiện thao tác này.',
  SUPABASE_NOT_CONFIGURED: 'Ứng dụng chưa được cấu hình kết nối Supabase.',
  DATA_NOT_FOUND: 'Không tìm thấy dữ liệu yêu cầu.',
  RECOVERY_SESSION_MISSING:
    'Phiên đặt lại mật khẩu không tồn tại. Hãy mở lại liên kết mới nhất trong email.',
  ACCOUNT_NOT_LINKED:
    'Tài khoản chưa được liên kết với hồ sơ. Vui lòng liên hệ quản trị viên.',
  PASSWORD_SETUP_NOT_ALLOWED:
    'Phiên này không được phép đặt mật khẩu. Hãy mở lại liên kết mới nhất trong email.',
  PASSWORD_MISMATCH: 'Mật khẩu xác nhận không khớp.',
  WEAK_PASSWORD:
    'Mật khẩu chưa đủ mạnh. Hãy dùng ít nhất 8 ký tự và tránh mật khẩu phổ biến.',
  SAME_PASSWORD: 'Mật khẩu mới phải khác mật khẩu hiện tại.',
  DEFAULT_PASSWORD_NOT_ALLOWED: 'Hãy chọn mật khẩu mới khác mật khẩu mặc định.',
  PASSWORD_CHANGE_REQUIRED: 'Bạn cần đổi mật khẩu mặc định trước khi tiếp tục.',
  RECOVERY_LINK_INVALID:
    'Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.',
};

export function errorMessage(
  code: unknown,
  fallback = 'Không thể thực hiện thao tác.',
) {
  return typeof code === 'string'
    ? (ERROR_MESSAGES[code] ?? fallback)
    : fallback;
}

export async function responseError(response: Response, fallback?: string) {
  try {
    const payload = (await response.clone().json()) as {
      error?: unknown;
      reason?: unknown;
    };
    return errorMessage(payload.error ?? payload.reason, fallback);
  } catch {
    return fallback ?? 'Không thể kết nối máy chủ.';
  }
}
