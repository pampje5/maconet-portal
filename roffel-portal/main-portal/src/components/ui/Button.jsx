export default function Button({
  variant = "primary",
  className = "",
  disabled = false,
  children,
  ...props
}) {
  const base = `
    inline-flex items-center justify-center
    rounded
    font-medium
    focus:outline-none
    focus:ring-2
    transition
    disabled:opacity-50
    disabled:cursor-not-allowed
  `;

  const variants = {
    primary: `
      px-6 py-2
      bg-blue-600 hover:bg-blue-700
      text-white
      focus:ring-blue-300
    `,
    secondary: `
      px-5 py-2
      border border-gray-300
      bg-white
      text-gray-700
      hover:bg-gray-100
      focus:ring-gray-200
    `,
    success: `
      px-6 py-2
      bg-green-600 hover:bg-green-700
      text-white
      focus:ring-green-300
    `,
    danger: `
      px-5 py-2
      border border-red-600
      bg-white
      text-red-600
      hover:bg-red-50
      focus:ring-red-300
    `,
  };

  return (
    <button
      {...props}
      disabled={disabled}
      className={`${base} ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
}
