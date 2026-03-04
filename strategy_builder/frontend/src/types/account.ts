/**
 * Account Types
 */

export interface AccountInfo {
  account_no: string;
  account_no_full: string;
  account_type: string;
  prod_code: string;
  is_vps: boolean;
  mode: string;
}

export interface Holding {
  stock_code: string;
  stock_name: string;
  quantity: number;
  avg_price: number;
  current_price: number;
  eval_amount: number;
  profit_loss: number;
  profit_rate: number;
}

export interface Balance {
  deposit: number;
  total_eval: number;
  purchase_amount: number;
  eval_amount: number;
  profit_loss: number;
  deposit_formatted?: string;
  total_eval_formatted?: string;
  profit_loss_formatted?: string;
}

export interface BuyableInfo {
  stock_code: string;
  price: number;
  amount: number;
  quantity: number;
  amount_formatted?: string;
}
